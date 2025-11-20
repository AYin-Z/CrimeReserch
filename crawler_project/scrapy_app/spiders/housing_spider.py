from __future__ import annotations

from typing import Optional

import scrapy

from crawler_project.scrapy_app.items import HousingItem

LIST_URL = "https://bj.lianjia.com/ershoufang/pg{page}/"


class LianjiaHousingSpider(scrapy.Spider):
    name = "housing_market"
    allowed_domains = ["bj.lianjia.com"]
    custom_settings = {"DOWNLOAD_DELAY": 2.5}

    def __init__(self, max_pages: int = 20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.table_name = "housing_market"

    def start_requests(self):
        for page in range(1, self.max_pages + 1):
            yield scrapy.Request(LIST_URL.format(page=page), callback=self.parse)

    def parse(self, response):
        for card in response.css("li.clear"):
            info = card.css(".houseInfo::text").get(default="").split("|")
            area = info[1].strip() if len(info) > 1 else None
            yield HousingItem(
                community=card.css(".positionInfo a::text").get(default="").strip(),
                address=card.css(".positionInfo a::attr(title)").get(),
                price=card.css(".totalPrice span::text").get(),
                unit_price=card.css(".unitPrice span::text").get(),
                area=area,
                deal_date=card.css(".dealDate::text").get(default="").strip(),
                latitude=None,
                longitude=None,
            )
