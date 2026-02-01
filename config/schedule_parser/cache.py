from dataclasses import dataclass

@dataclass(frozen=True)
class CacheConfig:
    CACHE_DIR: str = ".session_cache"
    COOKIES_FILE: str = "cookies.json"

cache_config = CacheConfig()