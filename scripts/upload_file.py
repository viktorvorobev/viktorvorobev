# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydrive2",
# ]
# ///
import argparse
import json
import logging
import sys

from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive, GoogleDriveFile

logging.basicConfig(
    stream=sys.stdout,
    format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
    level=logging.INFO,
)

logger = logging.getLogger()


class FileUploadError(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for uploading or updating existing file on Google Drive."
        "Credentials should be passed stored in 'credentials.json' file."
    )
    parser.add_argument(
        "--folder_id",
        required=True,
        help="ID of the folder that Service Account has access to, and where the file will be stored",
    )
    parser.add_argument(
        "--file_name",
        required=True,
        help="File name that will be updated/uploaded to the Google Drive",
    )
    parser.add_argument(
        "--credentials_json",
        required=True,
        help="Credentials as a JSON string",
    )
    return parser.parse_args()


def authenticate(credentials: dict) -> GoogleDrive:
    logger.info("Authenticating to Google Drive")
    try:
        gauth = GoogleAuth()
        gauth.auth_method = "service"
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials, ["https://www.googleapis.com/auth/drive"]
        )
        drive = GoogleDrive(gauth)
    except Exception as err:
        logger.error("Failed to authenticate to Google Drive. %s: %s", err.__class__.__name__, err)
        raise FileUploadError from err

    auth_info = drive.GetAbout()
    auth_success = auth_info["user"]["isAuthenticatedUser"]
    if not auth_success:
        logger.error("Failed to authenticate to Google Drive. User not authenticated")
        raise FileUploadError
    logger.info("Authenticated as %s", auth_info["user"]["displayName"])
    return drive


def get_file(drive: GoogleDrive, folder_id: str, file_name: str) -> GoogleDriveFile:
    # Check if file name already exists in folder.
    logger.info("Looking through the directory")
    file_list = drive.ListFile({"q": f'"{folder_id}" in parents and title="{file_name}" and trashed=false'}).GetList()

    # If file is found, update it, otherwise create new file.
    if len(file_list) == 1:
        logger.info("Found existing file")
        my_file = file_list[0]
    else:
        logger.info("File not found, creating a new one")
        my_file = drive.CreateFile(
            metadata={
                "parents": [{"kind": "drive#fileLink", "id": folder_id}],
                "title": file_name,
            }
        )
    return my_file


def upload_updated_file(file: GoogleDriveFile, file_name: str) -> None:
    logger.info("Updating file contents")
    file.SetContentFile(file_name)
    logger.info("Uploading updated file to Google Drive")
    file.Upload()
    logger.info("Upload completed")


if __name__ == "__main__":
    args = parse_args()

    try:
        credentials = json.loads(args.credentials_json)
    except json.JSONDecodeError as err:
        logger.error("Failed to parse credentials JSON. %s: %s", err.__class__.__name__, err)
        sys.exit(1)

    try:
        gdrive = authenticate(credentials=credentials)
        cv_file = get_file(gdrive, folder_id=args.folder_id, file_name=args.file_name)
        upload_updated_file(cv_file, file_name=args.file_name)
    except FileUploadError as err:
        logger.error("Something went wrong. %s: %s", err.__class__.__name__, err)
        sys.exit(1)
