import os
import shutil 
import sys
from time import time
from pprint import pprint

# local
import settings

# third party
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

service = None

def drive_authenticate():
    global service
    try:
        credentials = Credentials.from_service_account_file(
            settings.service_account_filepath, 
            scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(e)
        sys.exit(1)

def create_new_backup():
    print("Creating new world backup...")
    world_dir = os.path.join(settings.minecraft_path, "saves", settings.world_filename)
    try:
        shutil.make_archive(settings.world_filename, "zip", world_dir)
    except Exception as e:
        print("Error: failed to create a world backup")
        print(e)
        sys.exit(1)

def remove_old_backup():
    print("Removing old backup file...")
    response = service.files().list(
        q=f"trashed = false and name contains 'OLD_{settings.world_filename}' and mimeType contains 'zip'",
        spaces="drive",
        fields="files(id, name, mimeType)").execute()

    found_files = response['files']

    for file in found_files:
        print(f"Found file {file['name']}")

    # TODO(shaw): if multiple OLD backups are found, maybe just move the oldest one to trash???
    # or perhaps move all of them to trash except the newest one???

    if len(found_files) == 0:
        print(f"Failed to locate file with name OLD_{settings.world_filename}")
        return None

    if len(found_files) > 1:
        print(f"Warning: Found more than 1 file with name OLD_{settings.world_filename}")
        return None

    file_id = found_files[0]['id']
    file_name = found_files[0]['name']

    try:
        response = service.files().update(
            fileId=file_id, 
            body={"trashed": True}).execute()
    except HttpError as e:
        print("Failed to move old backup file to trash:")
        return None

    if response:
        if 'name' in response:
            print(f"Moved {response['name']} to trash")
        else:
            print("Could not find name of file moved to trash in response:")
            print(response)
    else: 
        print(f"Error: Failed to move file {file_name} to trash")


def rename_current_to_old():
    print("Renaming current backup file to OLD_<filename>...")
    response = service.files().list(
        q=f"trashed = false and name contains '{settings.world_filename}' and mimeType contains 'zip'",
        spaces="drive",
        fields="files(id, name, mimeType)").execute()

    found_files = []

    for file in response['files']:
        print(f"Found file {file['name']}")
        if 'OLD' not in file['name']:
            found_files.append(file)

    if len(found_files) == 0:
        print(f"Failed to locate file with name {settings.world_filename}")
        return None

    if len(found_files) > 1:
        print(f"Warning: Found more than 1 file with name {settings.world_filename}")
        return None

    file_id = found_files[0]['id']
    file_name = found_files[0]['name']

    try:
        response = service.files().update(
            fileId=file_id, 
            body={"name": f"OLD_{file_name}"}).execute()
    except HttpError as e:
        print(e)
        return None

    if response:
        if 'name' in response:
            print(f"Renamed {file_name} to {response['name']}")
        else:
            print("Could not find name of renamed file in response:")
            print(response)
    else: 
        print(f"Error: Failed to rename {file_name} to OLD_{file_name}")


def upload_backup():
    filename = settings.world_filename + ".zip"
    file_metadata = {
        'name': filename,
        'parents': [settings.dest_folder] }

    media = MediaFileUpload(
        filename,
        mimetype='application/zip',
        chunksize=256*1024*200, # must be a multiple of 256KB
        resumable=True)

    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id')

    response = None

    print("Starting upload...")
    while response == None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"    uploaded {int(status.progress() * 100)}%") 
        except HttpError as e:   
            print(e)
            sys.exit(1)

    #         if e.resp.status == 404:     
                # # Start the upload all over again.   
            # elif e.resp.status in [500, 502, 503, 504]:     
                # # Call next_chunk() again, but use an exponential backoff for repeated errors.   
            # else:     
    #             # Do not retry. Log the error and fail.

    print("Upload Complete!")

def remove_local_backup():
    filename = settings.world_filename + ".zip"
    print(f"Removing local backup: {filename}")
    try:
        os.remove(filename)
    except Exception as e:
        print("Error: Failed to remove local backup")
        print(e)


if __name__ == "__main__":
    start_time = time()
    create_new_backup()
    drive_authenticate()
    remove_old_backup()
    rename_current_to_old()
    upload_backup()
    remove_local_backup()
    print(f"Execution time: {time() - start_time} seconds")




