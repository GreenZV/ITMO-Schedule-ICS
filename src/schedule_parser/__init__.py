import json
import sys
import time
import logging
from pathlib import Path

from config.schedule_parser import schedule_parser_config
from src.schedule_parser.cache import SessionCache
from src.schedule_parser.authentification import Authentification
from src.schedule_parser.api import APIClient, APIResponse
from src.utils.deep_merge import json_file_merge

logger = logging.getLogger(__name__)

class ScheduleParser:
    def __init__(self):
        self.cache: SessionCache = SessionCache()
        self.api_client: APIClient = APIClient()
        self.api_response: APIResponse = APIResponse(
            success=False,
            data="",
            status_code=0,
            response_time=0,
            cookies_count=0
        )

    def parse(self) -> APIResponse:
        logger.info("Parser started")
        logger.info("Checking cached cookies...")
        cached_cookies = self.cache.load()

        if cached_cookies:
            logger.info("Cached cookies found")

            self.api_response = self.api_client.fetch(
                cookies=cached_cookies,
            )

            if self.api_response.success:
                logger.info("Cached cookies are valid")
                logger.info(f"The data has been received: {self.api_response.status_code}")
                logger.info(f"Response time: {self.api_response.response_time}")
                return self.api_response

            logger.warning(f"Cached cookies are invalid: {self.api_response.error}")
            self.cache.clear()

        logger.info("Obtaining new cookies using Selenium...")

        authentication = Authentification()
        cookies = authentication.login()

        if not cookies:
            logger.error("Selenium did not return cookies")
            sys.exit(1)

        self.api_response = self.api_client.fetch(
            cookies=cookies,
        )

        if self.api_response.success:
            self.cache.save(cookies, {
                "auth_time": time.time(),
                "source": "selenium_retry"
            })
        else:
            raise Exception(f"API error after re-authentication: {self.api_response.error}")

        logger.info(f"The data has been received: {self.api_response.status_code}")
        logger.info(f"Response time: {self.api_response.response_time}")
        return self.api_response

    def save(self, merge: bool = True) -> Path:
        data_dir = Path(schedule_parser_config.RESULT_DIR)
        data_dir.mkdir(exist_ok=True)

        data_path = data_dir / schedule_parser_config.RESULT_FILE
        data = self.api_response.data

        if merge:
            success = json_file_merge(str(data_path), data, indent=2)
            if success:
                logger.info("Data has been successfully merged and saved")
            else:
                logger.error("Error while merging data saving without merge")
                with open(data_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"The result has been saved: {data_path}")
        return data_path