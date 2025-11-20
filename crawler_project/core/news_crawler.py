"""News crawler targeting regional portals like north-news.cn."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..utils.data_parser import detect_disaster_type, extract_loss_info, parse_date
from .base_crawler import BaseCrawler

BASE_URL = "http://www.north-news.cn/"


class NewsCrawler(BaseCrawler):
    name = "news"

    async def crawl(
        self,
        start_date: datetime,
        end_date: datetime,
        max_pages: int = 20,
    ) -> AsyncGenerator[dict, None]:
        page = 1
        while page <= max_pages:
            url = f"{BASE_URL}news/node_{page}.htm"
            html = await self.fetch_text(url)
            soup = BeautifulSoup(html, "lxml")
            for article in soup.select(".list li"):
                record = await self._parse_article(article, start_date, end_date)
                if record:
                    yield record
            page += 1

    async def _parse_article(self, article, start: datetime, end: datetime):
        title_el = article.select_one("a")
        date_node = article.select_one("span")
        if not title_el or not date_node:
            return None
        date_text = date_node.get_text(strip=True)
        publish_date = parse_date(date_text)
        if not publish_date or not (start <= publish_date <= end):
            return None
        detail_url = urljoin(BASE_URL, title_el["href"])
        detail_html = await self.fetch_text(detail_url)
        body = self._extract_body(detail_html)
        return {
            "title": title_el.get_text(strip=True),
            "url": detail_url,
            "publish_date": publish_date.isoformat(),
            "location": self._extract_location(body),
            "disaster_type": detect_disaster_type(body),
            "loss": extract_loss_info(body),
            "content": body,
        }

    def _extract_body(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        body = soup.select_one(".article") or soup.select_one("#article")
        return body.get_text("\n", strip=True) if body else ""

    def _extract_location(self, text: str) -> str:
        keywords = ["市", "区", "县"]
        for token in keywords:
            idx = text.find(token)
            if 0 < idx < 20:
                return text[idx - 20 : idx + 1]
        return ""
