import json

import time
import logging
from pathlib import Path
from typing import Dict, Optional

from config.schedule_parser.cache import cache_config

logger = logging.getLogger(__name__)

class SessionCache:    
    def __init__(self):
        cache_dir = Path(cache_config.CACHE_DIR)
        cache_dir.mkdir(exist_ok=True)
        self.cache_file_path = cache_dir / cache_config.COOKIES_FILE
    
    def save(
        self,
        cookies: Dict[str, str],
        metadata: Optional[Dict] = None
    ) -> None:
        cache_data = {
            "cookies": cookies,
            "saved_at": time.time(),
            "count": len(cookies),
            "metadata": metadata or {}
        }
        
        with open(self.cache_file_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"Cookies have been saved to the cache: {len(cookies)} items")
    
    def load(self) -> Optional[Dict[str, str]]:
        if not self.cache_file_path.exists():
            logger.debug("Сookies were not found in the cache")
            return None
        
        try:
            with open(self.cache_file_path, 'r') as f:
                cache_data = json.load(f)
            
            cookies = cache_data.get("cookies", {})
            
            if not cookies:
                logger.warning("Cookies cache is empty")
                return None
            
            logger.info(f"Cookies loaded from cache: {len(cookies)} items")
            return cookies
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    def clear(self) -> None:
        if self.cache_file_path.exists():
            self.cache_file_path.unlink()
            logger.info("Cached cookies have been cleared.")
    
    def get_info(self) -> Dict:
        if not self.cache_file_path.exists():
            return {"exists": False}
        
        try:
            with open(self.cache_file_path, 'r') as f:
                data = json.load(f)
            
            age = time.time() - data.get("saved_at", 0)
            
            return {
                "exists": True,
                "cookies_count": len(data.get("cookies", {})),
                "age_seconds": age,
                "age_human": f"{age:.0f} секунд",
                "saved_at": data.get("saved_at"),
                "metadata": data.get("metadata", {})
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}