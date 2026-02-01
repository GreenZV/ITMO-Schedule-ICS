from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from typing import Dict, Optional

from config.schedule_parser.authentification import authentification_config
from config.schedule_parser.selenium import selenium_config

logger = logging.getLogger(__name__)

class Authentification:
    def __init__(self):
        self.driver = None
    
    def login(self) -> Optional[Dict[str, str]]:
        logger.info(f"Authorization on {authentification_config.LOGIN_URL}")
        start_time = time.time()

        options = Options()
        if selenium_config.HEADLESS:
            options.add_argument("--headless=new")
        
        if selenium_config.WINDOW_SIZE:
            options.add_argument(f"--window_size={selenium_config.WINDOW_SIZE}")

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")

        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-client-side-phishing-detection")

        options.add_argument("--mute-audio")
        options.add_argument("--disable-logging")

        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        
        try:
            self.driver.get(authentification_config.LOGIN_URL)

            wait = WebDriverWait(self.driver, selenium_config.TIMEOUT)
            
            user_elem = wait.until(
                EC.presence_of_element_located((By.NAME, authentification_config.USERNAME_FIELD_NAME))
            )
            user_elem.clear()
            user_elem.send_keys(authentification_config.USERNAME)

            pass_elem = self.driver.find_element(By.NAME, authentification_config.PASSWORD_FIELD_NAME)
            pass_elem.clear()
            pass_elem.send_keys(authentification_config.PASSWORD)
            
            submit_btn = self.driver.find_element(By.NAME, authentification_config.SUBMIT_BUTTON_FIELD_NAME)
            submit_btn.click()
            

            wait.until(EC.url_to_be(authentification_config.ENDPOINT_URL))
            current_url = self.driver.current_url
            if not (current_url == authentification_config.ENDPOINT_URL):
                logger.warning("There may be an authentication error, current URL: %s", current_url)
            
            selenium_cookies = self.driver.get_cookies()
            cookies_dict = {}
            
            for cookie in selenium_cookies:
                cookies_dict[cookie["name"]] = cookie["value"]
            
            elapsed = time.time() - start_time
            logger.info(f"Authorization successful in {elapsed:.1f}с")
            logger.info(f"Cookies received: {len(cookies_dict)}")
            logger.info(f"Current URL: {current_url}")
            
            return cookies_dict
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.debug("Driver is closed.")
