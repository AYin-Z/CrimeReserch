from __future__ import annotations

import scrapy

from crawler_project.scrapy_app.items import LegalItem

BASE_URL = "https://www.bjcourt.gov.cn/bjws/bsal/"


class BeijingCourtSpider(scrapy.Spider):
    name = "legal_cases"
    allowed_domains = ["bjcourt.gov.cn"]
    custom_settings = {"DOWNLOAD_DELAY": 2.0}

    def __init__(self, max_pages: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.table_name = "legal_cases"

    def start_requests(self):
        for page in range(1, self.max_pages + 1):
            yield scrapy.Request(f"{BASE_URL}?page={page}", callback=self.parse)

    def parse(self, response):
        for node in response.css(".list li"):
            title = node.css("a::text").get(default="").strip()
            detail_url = response.urljoin(node.css("a::attr(href)").get(default=""))
            judgment_date = node.css("span::text").get(default="").strip()
            location = self._extract_location(title)
            yield LegalItem(
                title=title,
                judgment_date=judgment_date,
                case_type="刑事",
                location=location,
                charges=None,
                law_articles=None,
                url=detail_url,
            )

    def _extract_location(self, text: str):
        for suffix in ("法院", "区", "市"):
            idx = text.find(suffix)
            if idx > 0:
                start = max(0, idx - 6)
                return text[start : idx + len(suffix)]
        return None
