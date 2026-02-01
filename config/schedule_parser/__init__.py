from dataclasses import dataclass

@dataclass(frozen=True)
class ScheduleParserConfig:
    RESULT_DIR: str = "data"
    RESULT_FILE: str = "schedule.json"

schedule_parser_config = ScheduleParserConfig()