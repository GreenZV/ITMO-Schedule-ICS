import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthentificationConfig:
    LOGIN_URL: str = "https://my.itmo.ru/schedule"
    ENDPOINT_URL: str = "https://my.itmo.ru/schedule"

    USERNAME_FIELD_NAME: str = "username"
    PASSWORD_FIELD_NAME: str = "password"
    SUBMIT_BUTTON_FIELD_NAME: str = "login"

    USERNAME: str = os.getenv("USERNAME")
    PASSWORD: str = os.getenv("PASSWORD")

authentification_config = AuthentificationConfig()