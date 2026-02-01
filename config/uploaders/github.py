import os
from dataclasses import dataclass

@dataclass(frozen=True)
class GithubConfig:
    GITHUB_TOKEN: str = os.getenv("TOKEN")
    REPO: str = os.getenv("REPO")
    BRANCH: str = "main"

github_config = GithubConfig()