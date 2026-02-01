from dataclasses import dataclass

@dataclass(frozen=True)
class LogConfig:
    LEVEL: str = "INFO"
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"
    LOG_FILE: str = "schedule.log"

log_config = LogConfig()