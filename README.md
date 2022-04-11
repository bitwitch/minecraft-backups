# Minecraft Backups on Google Drive
I spend extended periods of time at different locations with different
computers. I used to have a minecraft server, but the price just wasn't worth
it. Now I just play minecraft locally and whenever I am going to switch to one
of my other locations, I just make a backup of my world, upload it to google
drive, and download it at the other location. I created this little utility to
automate that process.

The basic idea is to: 
- create a backup file of your minecraft world, for example `myworld.zip`
- search for a current backup on google drive named `myworld.zip`
- rename it to `OLD_myworld.zip`
- if there was already and `OLD_myworld.zip` move it to the trash first
- upload the new backup `myworld.zip`


## Usage
1. Create a file called `settings.py` and define the following variables:
```
minecraft_path = 'path_to_.minecraft_directory'
world_filename = 'name_of_world_directory'
service_account_filepath = 'service_account.json'
dest_folder = 'id_of_folder_on_google_drive_where_you_want_backups'
```
2. You will need a google drive service account with access to the directory
   where you want to upload backups. Export the credentials to a file like
   `service_account.json`. (Here is a link)[https://support.google.com/a/answer/7378726?hl=en] that basically describes how to do
   it.

3. Install dependencies, see references.txt. Unfortunately we have to use
   googles api client packages because there is no documentation for just
   making basic http requests and it would take way to much energy to figure it
   out for such a small throwaway project.

4. Exectute the program
`$ python backup.py`


## Helpful Links
(Drive Python API Docs)[https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.html]
