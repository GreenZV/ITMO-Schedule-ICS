import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from icalendar import Calendar, Event
import pytz

from config.calendar_generator.__init__ import calendar_generator_config

logger = logging.getLogger(__name__)

class CalendarsGenerator:
    def __init__(self):
        self.calendars: Dict[str, Calendar] = {}
        self.moscow_tz = pytz.timezone("Europe/Moscow")

    def _make_event(self, date_str: str, lesson: Dict[str, Any]) -> Event:
        event = Event()
        lesson_type = lesson.get("work_type")
        lesson_type_id = lesson.get("work_type_id")
        lesson_format = lesson.get("format", None)
        subject = lesson.get("subject")
        time_start = lesson.get("time_start")
        time_end = lesson.get("time_end")
        teacher = lesson.get("teacher_name", None)
        teacher_id = lesson.get("teacher_id", None)
        room = lesson.get("room", None)
        building = lesson.get("building", None)
        group = lesson.get("group", None)
        note = lesson.get("note", None)
        zoom_url = lesson.get("zoom_url", None)
        zoom_password = lesson.get("zoom_password", None)
        zoom_info = lesson.get("zoom_info", None)
        pair_id = lesson.get("pair_id")
        color = calendar_generator_config.COLORS.get(lesson_type_id)

        calendar_name = f"ITMO {lesson_type}"

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if time_start and time_end:
            start_time = datetime.strptime(time_start, "%H:%M").time()
            end_time = datetime.strptime(time_end, "%H:%M").time()

            start_dt = self.moscow_tz.localize(
                datetime.combine(date_obj, start_time)
            )
            end_dt = self.moscow_tz.localize(
                datetime.combine(date_obj, end_time)
            )
        else:
            start_dt = self.moscow_tz.localize(
                datetime.combine(date_obj, datetime.min.time())
            )
            end_dt = self.moscow_tz.localize(
                datetime.combine(date_obj, datetime.max.time())
            ) - timedelta(seconds=1)

        if calendar_name not in self.calendars:
            cal = Calendar()
            cal.add("prodid", "-//Schedule//")
            cal.add("version", "2.0")
            cal.add("name", calendar_name)
            cal.add("X-WR-CALNAME", calendar_name)
            cal.add("timezone", "Europe/Moscow")
            cal.add("X-APPLE-CALENDAR-COLOR", color)
            self.calendars[calendar_name] = cal

        event.add("summary", f"{subject} - {lesson_type}")

        description_parts = []
        if teacher:
            description_parts.append(f"Преподаватель: {teacher_id} {teacher}")
        if group:
            description_parts.append(f"Группа: {group}")
        if lesson_format:
            description_parts.append(f"Формат: {lesson_format}")
        if zoom_password:
            description_parts.append(f"Zoom Пароль: {zoom_password}")
        if zoom_info:
            description_parts.append(f"Zoom Информация: {zoom_info}")
        if note:
            description_parts.append(f"Примечание: {note}")

        event.add("description", "\n".join(description_parts))
        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)
        event.add("uid", f"{pair_id}@my.itmo.ru")

        location_parts = []
        if building or room:
            if building:
                location_parts.append(building)
            if room:
                location_parts.append(f"ауд. {room}")
            if zoom_url:
                event.add("url", zoom_url)
        elif zoom_url:
            location_parts.append(zoom_url)

        if location_parts:
            event.add("location", ", ".join(location_parts))

        self.calendars[calendar_name].add_component(event)
        return event

    def generate(self, data: Dict[str, Any]) -> Dict[str, Calendar]:
        logger.info("Calendar generator started")
        for date_str, lessons in data.items():
            for lesson in lessons:
                self._make_event(date_str=date_str, lesson=lesson)

        logger.info("Calendar generator finished")
        return self.calendars


    def save(self) -> Dict[str, Path]:
        calendar_dir = Path(calendar_generator_config.CALENDAR_DIR)
        calendar_dir.mkdir(parents=True, exist_ok=True)
        calendar_paths = {}

        for calendar_name, cal in self.calendars.items():
            calendar_path = calendar_dir / f"{calendar_name}.ics"
            calendar_paths[calendar_name] = calendar_path
            with open(calendar_path, "wb") as f:
                f.write(cal.to_ical())
        return calendar_paths
