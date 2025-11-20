from __future__ import annotations

from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import scrapy

from crawler_project.scrapy_app.items import NewsItem
from crawler_project.utils.data_parser import detect_disaster_type, extract_loss_info, parse_date

BASE_URL = "http://www.north-news.cn/"


class NorthNewsSpider(scrapy.Spider):
    name = "north_news"
    allowed_domains = ["north-news.cn"]
    custom_settings = {"DOWNLOAD_DELAY": 2.0}

    def __init__(self, start_date: str = "2011-01-01", end_date: str = "2020-12-31", max_pages: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = datetime.fromisoformat(start_date)
        self.end_date = datetime.fromisoformat(end_date)
        self.max_pages = int(max_pages)
        self.table_name = "news_events"

    def start_requests(self):
        for page in range(1, self.max_pages + 1):
            url = f"{BASE_URL}news/node_{page}.htm"
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        for article in response.css(".list li"):
            link = article.css("a::attr(href)").get()
            title = article.css("a::text").get(default="").strip()
            date_text = article.css("span::text").get(default="").strip()
            publish_date = parse_date(date_text)
            if not link or not publish_date:
                continue
            if publish_date < self.start_date or publish_date > self.end_date:
                continue
            detail_url = urljoin(response.url, link)
            yield response.follow(
                detail_url,
                callback=self.parse_detail,
                cb_kwargs={
                    "title": title,
                    "publish_date": publish_date,
                },
            )

    def parse_detail(self, response, title: str, publish_date: datetime):
        body_text = "\n".join(response.css(".article *::text, #article *::text").getall()).strip()
        content = body_text or " ".join(response.css("body ::text").getall()).strip()
        location = self._guess_location(content)
        yield NewsItem(
            title=title,
            url=response.url,
            publish_date=publish_date.isoformat(),
            disaster_type=detect_disaster_type(content),
            location=location,
            loss=extract_loss_info(content),
            content=content,
        )

    def _guess_location(self, text: str) -> Optional[str]:
        markers = ["市", "区", "县"]
        for marker in markers:
            idx = text.find(marker)
            if idx > 0:
                start = max(0, idx - 10)
                return text[start : idx + 1]
        return None
