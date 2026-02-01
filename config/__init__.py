from dataclasses import dataclass
from enum import Enum

class Uploader(Enum):
    GITHUB = 1
    DROPBOX = 2

@dataclass(frozen=True)
class Config:
    UPLOAD_WAY: Uploader = Uploader.DROPBOX

config = Config()