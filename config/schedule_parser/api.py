from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class ApiConfig:
    SPRING_TERM_START: datetime = datetime.strptime(f"{datetime.now().year}-02-01", "%Y-%m-%d")
    SPRING_TERM_END: datetime = datetime.strptime(f"{datetime.now().year}-07-01", "%Y-%m-%d")

    DATE_START: datetime = datetime.now()
    DATE_END: datetime = SPRING_TERM_END if (DATE_START >= SPRING_TERM_START) & (DATE_START < SPRING_TERM_END) else SPRING_TERM_START

    BASE_API_URL: str = "https://my.itmo.ru/api/schedule/schedule/personal?"
    API_URL: str = f"{BASE_API_URL}date_start={DATE_START.strftime('%Y-%m-%d')}&date_end={DATE_END.strftime('%Y-%m-%d')}"
    HEADERS: Dict[int, str] = field(default_factory=lambda: {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        })

api_config = ApiConfig()