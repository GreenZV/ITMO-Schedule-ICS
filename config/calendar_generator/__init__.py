from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class CalendarGeneratorConfig:
    CALENDAR_DIR: str = "calendars"
    COLORS: Dict[int, str] = field(default_factory=lambda: {
        1: "#0091ff",
        2: "#a50aff",
        3: "#f7b500",
        4: "#ee215b",
        5: "#ee215b",
        6: "#ee215b",
        7: "#ee215b",
        8: "#ee215b",
        9: "#ee215b",
        10: "#1846c7",
        11: "#22b217",
        12: "#22b217"
    })

calendar_generator_config = CalendarGeneratorConfig()