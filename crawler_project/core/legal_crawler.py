"""Crawler for Beijing court documents."""

from __future__ import annotations

from typing import AsyncGenerator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler

BASE_URL = "https://www.bjcourt.gov.cn/bjws/bsal/"  # Example listing page


class LegalCrawler(BaseCrawler):
    name = "legal"

    async def crawl(self, max_pages: int = 5) -> AsyncGenerator[dict, None]:
        for page in range(1, max_pages + 1):
            url = f"{BASE_URL}?page={page}"
            html = await self.fetch_text(url)
            soup = BeautifulSoup(html, "lxml")
            for row in soup.select(".list li"):
                record = await self._build_record(row)
                if record:
                    yield record

    async def _build_record(self, row):
        link = row.select_one("a")
        if not link:
            return None
        detail_url = urljoin(BASE_URL, link["href"])
        detail_html = await self.fetch_text(detail_url)
        detail = self._parse_detail(detail_html)
        return {
            "title": link.get_text(strip=True),
            "case_type": "刑事",
            "judgment_date": row.select_one("span").get_text(strip=True) if row.select_one("span") else None,
            "detail_url": detail_url,
            **detail,
        }

    def _parse_detail(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        body = soup.select_one(".article")
        text = body.get_text("\n", strip=True) if body else ""
        return {
            "location": self._extract_location(text),
            "charges": self._extract_charges(text),
            "statutes": self._extract_statutes(text),
            "content": text,
        }

    def _extract_location(self, text: str) -> str:
        markers = ["北京市", "区", "县"]
        for marker in markers:
            idx = text.find(marker)
            if idx != -1:
                return text[max(0, idx - 12) : idx + len(marker)]
        return ""

    def _extract_charges(self, text: str) -> str:
        keywords = ["盗窃", "故意伤害", "诈骗", "抢劫"]
        for kw in keywords:
            if kw in text:
                return kw
        return ""

    def _extract_statutes(self, text: str) -> str:
        start = text.find("《")
        end = text.find("法")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return ""
