import json
import logging
import sys
from pathlib import Path
from typing import Dict
import requests

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode, FileMetadata
from icalendar import Calendar

from config.calendar_generator import calendar_generator_config
from config.uploaders.dropbox import dropbox_config

logger = logging.getLogger(__name__)

class DropboxUploader:
    def __init__(self):
        logger.info("Initializing DropboxUploader")
        try:
            access_token = self._get_fresh_access_token()

            if not access_token:
                raise ValueError("Dropbox access token is not configured")

            logger.info("Creating Dropbox client")
            self.dbx = dropbox.Dropbox(
                access_token,
                timeout=dropbox_config.TIMEOUT if hasattr(dropbox_config, "TIMEOUT") else 30
            )

            self.dbx.users_get_current_account()
            logger.info("Successfully authenticated with Dropbox")

        except AuthError as e:
            logger.error(f"Dropbox authentication failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to initialize DropboxUploader: {e}")
            sys.exit(1)

    def _get_fresh_access_token(self):
        url = "https://api.dropboxapi.com/oauth2/token"

        response = requests.post(url, data={
            'grant_type': 'refresh_token',
            'refresh_token': dropbox_config.DROPBOX_REFRESH_TOKEN,
            'client_id': dropbox_config.DROPBOX_APP_KEY,
            'client_secret': dropbox_config.DROPBOX_APP_SECRET
        })

        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Failed to refresh token: {response.text}")

    def _check_folder(self, folder_path: str) -> bool:
        logger.info(f"Checking for existing folder: '{folder_path}'")
        try:
            self.dbx.files_get_metadata(folder_path)
            logger.info(f"Found existing folder: '{folder_path}'")
            return True
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                logger.info(f"Folder '{folder_path}' does not exist")
                return False
            else:
                logger.error(f"Error checking folder '{folder_path}': {e}")
                sys.exit(1)

    def _create_folder(self, folder_path: str) -> None:
        logger.info(f"Creating new folder: '{folder_path}'")
        try:
            self.dbx.files_create_folder_v2(folder_path)
            logger.info(f"Folder '{folder_path}' created successfully")
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_conflict():
                logger.info(f"Folder '{folder_path}' already exists (concurrent creation)")
            else:
                logger.error(f"Error creating folder '{folder_path}': {e}")
                sys.exit(1)

    def _get_direct_download_link(self, file_path_str: str) -> str:
        logger.info(f"Getting direct download link for: '{file_path_str}'")
        try:
            shared_link_metadata = self.dbx.sharing_create_shared_link_with_settings(
                file_path_str,
                settings=None
            )

            direct_link = shared_link_metadata.url
            direct_link = direct_link.replace("www.dropbox.com", "dl.dropboxusercontent.com")
            direct_link = direct_link.replace("?dl=0", "?dl=1")

            if "?dl=1" not in direct_link:
                if '?' in direct_link:
                    direct_link += "&dl=1"
                else:
                    direct_link += "?dl=1"

            logger.info(f"Generated permanent direct download link for '{file_path_str}'")
            return direct_link

        except ApiError as e:
            if e.error.is_shared_link_already_exists():
                links = self.dbx.sharing_list_shared_links(
                    path=file_path_str,
                    direct_only=True
                )
                if links.links:
                    direct_link = links.links[0].url
                    direct_link = direct_link.replace("www.dropbox.com", "dl.dropboxusercontent.com")
                    direct_link = direct_link.replace("?dl=0", "?dl=1")
                    if "?dl=1" not in direct_link:
                        direct_link += "?dl=1"
                    return direct_link

            logger.error(f"Failed to get download link for '{file_path_str}': {e}")
            sys.exit(1)

    def _upload_or_update_file(self, content: bytes, file_path_str: str) -> str:
        logger.info(f"Processing file: '{file_path_str}'")

        try:
            mode = WriteMode.overwrite

            result = self.dbx.files_upload(
                content,
                file_path_str,
                mode=mode,
                autorename=False
            )

            logger.info(f"Successfully uploaded file: '{file_path_str}'")

            direct_link = self._get_direct_download_link(file_path_str)

            return direct_link

        except ApiError as e:
            logger.error(f"Failed to upload file '{file_path_str}': {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error processing file '{file_path_str}': {e}")
            sys.exit(1)

    def _check_existing_file(self, dropbox_path: str) -> bool:
        logger.info(f"Checking for existing file: '{dropbox_path}'")
        try:
            self.dbx.files_get_metadata(dropbox_path)
            logger.info(f"File exists: '{dropbox_path}'")
            return True
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                logger.info(f"File does not exist: '{dropbox_path}'")
                return False
            else:
                logger.error(f"Error checking file '{dropbox_path}': {e}")
                sys.exit(1)

    def upload(self, calendars: Dict[str, Calendar], calendars_paths: Dict[str, Path]) -> Dict[str, str]:
        logger.info(f"Starting Dropbox upload of {len(calendars)} calendar(s)")

        try:
            folder_name = calendar_generator_config.CALENDAR_DIR
            folder_name = folder_name.strip('/')
            folder_path = f"/{folder_name}"

            logger.info(f"Using Dropbox folder path: {folder_path}")

            if not self._check_folder(folder_path):
                self._create_folder(folder_path)

            download_urls = {}

            for calendar_name in calendars:
                file_path = calendars_paths[calendar_name]
                file_path_str = str(file_path).replace('\\', '/')
                file_path_str = f"/{file_path_str}"
                content = calendars[calendar_name].to_ical()

                logger.info(f"Processing calendar: '{calendar_name}' from file: {file_path.name}")

                file_exists = self._check_existing_file(file_path_str)

                if file_exists:
                    logger.info(f"File exists, updating: '{file_path.name}'")
                else:
                    logger.info(f"Creating new file: '{file_path.name}'")

                download_url = self._upload_or_update_file(content, file_path_str)
                download_urls[calendar_name] = download_url

            logger.info(f"Dropbox upload completed. Generated {len(download_urls)} direct download URL(s)")
            return download_urls

        except Exception as e:
            logger.error(f"Failed during Dropbox upload process: {e}")
            sys.exit(1)