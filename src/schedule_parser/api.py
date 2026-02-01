from datetime import datetime

import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from config.schedule_parser.api import api_config

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    success: bool
    data: Any
    status_code: int
    response_time: float
    cookies_count: int
    error: Optional[str] = None

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(api_config.HEADERS)

    def set_cookies(
        self,
        cookies: Dict[str, str]
    ) -> None:
        self.session.cookies.clear()
        self.session.cookies.update(cookies)
        logger.info(f"Cookies have been set: {len(cookies)} items")
    
    def request(
        self,
        authorization_token: str
    ) -> APIResponse:
        start_time = time.time()
        
        try:
            logger.info(f"GET -> {api_config.API_URL}")

            response = self.session.get(
                api_config.API_URL,
                headers={
                    "Authorization": authorization_token
                },
                allow_redirects=False,
                stream=True
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = response.text
                
                return APIResponse(
                    success=True,
                    data=response_data,
                    status_code=200,
                    response_time=response_time,
                    cookies_count=len(self.session.cookies)
                )
            
            elif response.status_code == 401:
                return APIResponse(
                    success=False,
                    data=None,
                    status_code=401,
                    response_time=response_time,
                    cookies_count=len(self.session.cookies),
                    error="Session expired (401)"
                )
            
            elif response.status_code == 403:
                return APIResponse(
                    success=False,
                    data=None,
                    status_code=403,
                    response_time=response_time,
                    cookies_count=len(self.session.cookies),
                    error="Forbidden (403)"
                )
            
            else:
                return APIResponse(
                    success=False,
                    data=response.text[:500] if response.text else None,
                    status_code=response.status_code,
                    response_time=response_time,
                    cookies_count=len(self.session.cookies),
                    error=f"HTTP {response.status_code}"
                )
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout after 30s"
            logger.error(error_msg)
            return APIResponse(
                success=False,
                data=None,
                status_code=0,
                response_time=time.time() - start_time,
                cookies_count=len(self.session.cookies),
                error=error_msg
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            logger.error(error_msg)
            return APIResponse(
                success=False,
                data=None,
                status_code=0,
                response_time=time.time() - start_time,
                cookies_count=len(self.session.cookies),
                error=error_msg
            )
    
    def fetch(self, cookies: Dict[str, str]) -> APIResponse:
        self.set_cookies(cookies)

        authorization = cookies["auth._token.itmoId"].replace("%20", ' ')

        logger.info("Fetching data")
            
        response = self.request(authorization)
        
        return response