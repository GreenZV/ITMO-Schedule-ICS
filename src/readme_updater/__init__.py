import logging
from datetime import datetime
from typing import Dict

from config.readme_updater import readme_updater_config

logger = logging.getLogger(__name__)

class ReadMeUpdater:
    def _generate_subscription_links(self, download_url: str, calendar_name: str) -> str:
        links_markdown = ""
        for service, data in readme_updater_config.CALENDAR_APPS.items():
            download_url_clean = download_url.replace("https://", "").replace("http://", "")
            url = data["url"].format(download_url=download_url, calendar_name=calendar_name, download_url_clean=download_url_clean).replace(" ", "%20")
            icon = data["icon"]
            protocol = data["protocol"]
            if protocol == "https" or protocol == "http":
                links_markdown += f"[{icon} {service}]({url})\n\n"
            else:
                links_markdown += f"{icon} {service}\n\n`{url}`\n\n"

        return links_markdown

    def _generate_calendar_section(self, calendar_name: str, download_url: str) -> str:
        subscription_links = self._generate_subscription_links(download_url, calendar_name)
        additional_links = f"📥 Прямая загрузка\n\n{download_url.replace(' ', '%20')}"

        section = f"""
### 📅 {calendar_name}

#### 🔗 Ссылки для подписки
{subscription_links}

#### 📎 Дополнительные ссылки
{additional_links}
"""
        return section.strip()

    def update_readme(self, calendar_links: Dict[str, str]) -> None:
        logger.info(f"Обновление README с {len(calendar_links)} календарями...")

        content = "# ITMO Schedule ICS\n\n"
        content += f"{readme_updater_config.CONTENT_LIST}\n\n"

        content += "## 📅 Календари для подписки\n\n"
        content += "*Автоматически обновляемые iCalendar (.ics) файлы*\n\n"

        content += f"**🔄 Последнее обновление:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}`\n"
        content += f"**📊 Количество календарей:** `{len(calendar_links)}`\n\n"

        content += "---\n\n"

        for calendar_name, url in calendar_links.items():
            content += self._generate_calendar_section(calendar_name, url)
            content += "\n\n---\n\n"

        content += readme_updater_config.SETUP_GUIDES
        content += "\n"
        content += readme_updater_config.TROUBLESHOOTING
        content += "\n"
        content += readme_updater_config.START_GUIDE

        with open(readme_updater_config.README_FILE, 'w', encoding="utf-8") as f:
            f.write(content)