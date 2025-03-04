# Upload files to Google Drive

This is a helper script that allows you to upload files to a Google Drive using a service account.

## Setup

1. Create a service account
   1. Go to https://console.cloud.google.com/
   2. Create a new project
   3. Go to "APIs & Services" &rarr; "Enable APIs and services"
   4. Search for Google Drive API, select it and click "Enable"
   5. Then click "Create credentials"
      - You will be accessing the "User data"
      - Fill in all the required emails, etc.
      - When creating OAuth Client ID select "Desktop app"
   6. Go to credentials
   7. Create service account and grant it permissions to google drive
2. Create a folder on Google Drive  
   As a result of previous step you'll get a "Service account".
   You must allow it "Redactor" permissions, so it will be able to upload new
   files and modify existing files.
3. Put `credentials.json` file into the same folder as the `upload_file.py` script
4. Use script as follows:
   ```bash
   python upload_file.py --folder_id $FOLDER_ID --file_name example.txt
   ```

## Run script

1. [Get `uv`](https://docs.astral.sh/uv/getting-started/installation/)
2. Run script
   ```bash
   uv run upload_file.py --folder_id $FOLDER_ID --file_name example.txt
   ```
   Where `$FOLDER_ID` can be get from the URL to the Google Drive.
   E.g. for `https://drive.google.com/drive/u/0/folders/1Ug82tk8ilDiITHGsjtmDHC3dGtz97IIo`
   the folder ID would be `1Ug82tk8ilDiITHGsjtmDHC3dGtz97IIo`
