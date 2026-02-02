import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

from config.schedule_parser import schedule_parser_config
from src.schedule_parser.cache import SessionCache
from src.schedule_parser.authentification import Authentification
from src.schedule_parser.api import APIClient, APIResponse

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

    def _merge_data(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Any:
        result = existing.copy()
        result.update(new)
        return result

    def _json_file_merge(self, file_path: str, new_data: Dict[str, Any], indent: int = 2) -> bool:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf-8") as f:
                    existing_data = json.load(f)
                merged_data = self._merge_data(existing_data, new_data)
            else:
                merged_data = new_data

            with open(file_path, 'w', encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=indent)

            return True

        except json.JSONDecodeError:
            with open(file_path, 'w', encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=indent)
            return True

        except Exception:
            return False

    def save(self, merge: bool = True) -> Path:
        data_dir = Path(schedule_parser_config.RESULT_DIR)
        data_dir.mkdir(exist_ok=True)

        data_path = data_dir / schedule_parser_config.RESULT_FILE
        data = self.api_response.data

        if merge:
            success = self._json_file_merge(str(data_path), data, indent=2)
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