import logging
import sys
from pathlib import Path

from github import Github
from icalendar import Calendar
from typing import Dict

from config.uploaders.github import github_config

logger = logging.getLogger(__name__)

class GitHubUploader:
    def __init__(self):
        logger.info("Initializing GitHubUploader")
        try:
            logger.info(f"Connecting to GitHub repository: {github_config.REPO} on branch: {github_config.BRANCH}")
            self.github = Github(github_config.GITHUB_TOKEN)
            self.repo_name = github_config.REPO
            self.repo = self.github.get_repo(self.repo_name)
            self.branch = github_config.BRANCH
            logger.info(f"Successfully connected to repository: {self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GitHubUploader: {e}")
            sys.exit(1)

    def upload(self, calendars: Dict[str, Calendar], calendars_paths: Dict[str, Path]):
        logger.info(f"Starting upload of {len(calendars)} calendar(s)")
        download_urls = {}

        for calendar_name in calendars:
            file_path = calendars_paths[calendar_name]
            file_path_str = str(file_path).replace("\\", "/")

            logger.info(f"Processing calendar: {calendar_name} at path: {file_path_str}")

            try:
                content = calendars[calendar_name].to_ical()
                logger.info(f"Calendar '{calendar_name}' encoded to iCal format")

                try:
                    existing_file = self.repo.get_contents(file_path_str, ref=self.branch)
                    logger.info(f"File exists, updating: {file_path_str}")

                    self.repo.update_file(
                        path=file_path_str,
                        message=f"Update {file_path.name}",
                        content=content,
                        sha=existing_file.sha,
                        branch=self.branch
                    )
                    logger.info(f"Successfully updated file: {file_path_str}")

                except Exception as e:
                    if "404" in str(e):
                        logger.info(f"File does not exist, creating new: {file_path_str}")
                    else:
                        logger.warning(f"Error when checking file existence: {e}, attempting to create new file")

                    self.repo.create_file(
                        path=file_path_str,
                        message=f"Add {file_path.name}",
                        content=content,
                        branch=self.branch
                    )
                    logger.info(f"Successfully created new file: {file_path_str}")

                download_url = f"https://raw.githubusercontent.com/{self.repo_name}/{self.branch}/{file_path_str}"
                download_urls[calendar_name] = download_url
                logger.info(f"Generated download URL for '{calendar_name}'")

            except Exception as e:
                logger.error(f"Failed to upload calendar '{calendar_name}': {e}")
                sys.exit(1)

        logger.info(f"Upload completed. Generated {len(download_urls)} download URL(s)")
        return download_urls