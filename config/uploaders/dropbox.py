import os
from dataclasses import dataclass

@dataclass(frozen=True)
class DropboxConfig:
    DROPBOX_REFRESH_TOKEN: str = os.getenv("DROPBOX_REFRESH_TOKEN")
    DROPBOX_APP_KEY: str = os.getenv("DROPBOX_APP_KEY")
    DROPBOX_APP_SECRET: str = os.getenv("DROPBOX_APP_SECRET")

dropbox_config = DropboxConfig()