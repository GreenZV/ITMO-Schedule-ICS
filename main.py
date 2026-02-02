import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from config import Uploader, config
from config.logging import log_config
from src.calendar_generator import CalendarsGenerator
from src.readme_updater import ReadMeUpdater
from src.schedule_parser import ScheduleParser

if config.UPLOAD_WAY == Uploader.GITHUB:
    from src.uploaders.github import GitHubUploader
if config.UPLOAD_WAY == Uploader.DROPBOX:
    from src.uploaders.dropbox import DropboxUploader

load_dotenv()

log_dir = Path(log_config.LOG_DIR)
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, log_config.LEVEL),
    format=log_config.FORMAT,
    handlers=[
        logging.FileHandler(log_dir / log_config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Program started")
    logger.info("=" * 60)

    try:
        parser = ScheduleParser()
        response = parser.parse()
        data_path = parser.save()
        schedule_parser_time = time.time() - start_time
    except Exception as e:
        logger.error(f"Schedule parser failed with error: {e}")
        sys.exit(1)

    try:
        generator = CalendarsGenerator()
        calendars = generator.generate(response.data)
        calendars_paths = generator.save()
        calendars_generator_time = time.time() - schedule_parser_time
    except Exception as e:
        logger.error(f"Calendar generator failed with error: {e}")
        sys.exit(1)

    if config.UPLOAD_WAY == Uploader.GITHUB:
        uploader = GitHubUploader()
    elif config.UPLOAD_WAY == Uploader.DROPBOX:
        uploader = DropboxUploader()
    else:
        logger.error(f"Unknown upload way: {config.UPLOAD_WAY}")
        sys.exit(1)

    try:
        calendar_links = uploader.upload(calendars, calendars_paths)
        uploader_time = time.time() - schedule_parser_time - calendars_generator_time
    except Exception as e:
        logger.error(f"Uploader failed with error: {e}")
        sys.exit(1)

    try:
        readme_updater = ReadMeUpdater()
        readme_updater.update_readme(calendar_links)
        readme_updater_time = time.time() - schedule_parser_time - calendars_generator_time - uploader_time
    except Exception as e:
        logger.error(f"Readme updater failed with error: {e}")
        sys.exit(1)

    total_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info("Program finished")
    logger.info(f"Schedule parser took: {schedule_parser_time}: seconds")
    logger.info(f"Calendar generator took: {calendars_generator_time}: seconds")
    logger.info(f"Uploader took: {uploader_time}: seconds")
    logger.info(f"Readme updater took: {readme_updater_time} seconds")
    logger.info(f"Total time taken: {total_time} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()