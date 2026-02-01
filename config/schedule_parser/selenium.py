from dataclasses import dataclass

@dataclass(frozen=True)
class SeleniumConfig:
    HEADLESS: bool = True
    WINDOW_SIZE: str = "1200,800"
    TIMEOUT: int = 60

selenium_config = SeleniumConfig()