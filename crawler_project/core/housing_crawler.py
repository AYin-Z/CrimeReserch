"""Crawler for housing data from Lianjia."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

from pyquery import PyQuery as pq

from .base_crawler import BaseCrawler
from ..utils.browser import fetch_dynamic_html

LIST_URL = "https://bj.lianjia.com/ershoufang/pg{page}/"


class HousingCrawler(BaseCrawler):
    name = "housing"

    async def crawl(self, max_pages: int = 100) -> AsyncGenerator[dict, None]:
        for page in range(1, max_pages + 1):
            url = LIST_URL.format(page=page)
            html = await asyncio.to_thread(fetch_dynamic_html, url)
            for record in self._parse_page(html):
                yield record

    def _parse_page(self, html: str):
        doc = pq(html)
        for item in doc("li.clear").items():
            yield {
                "community": item.find(".positionInfo a").text(),
                "address": item.find(".positionInfo a").attr("title"),
                "price": item.find(".totalPrice span").text(),
                "area": item.find(".houseInfo").text(),
                "deal_date": item.find(".dealDate").text(),
            }
