from __future__ import annotations

import json
from typing import Tuple
from urllib.parse import urlencode

import scrapy

from crawler_project.config import settings as project_settings
from crawler_project.scrapy_app.items import PoiItem

BAIDU_POI_URL = "http://api.map.baidu.com/place/v2/search"


def _parse_bounds(bounds: str) -> Tuple[str, str]:
    southwest, northeast = bounds.split(";")
    return southwest, northeast


class BaiduPoiSpider(scrapy.Spider):
    name = "spatial_poi"
    allowed_domains = ["api.map.baidu.com"]
    custom_settings = {"DOWNLOAD_DELAY": 1.0}

    def __init__(self, category: str = "学校", bounds: str = "39.5,116.2;41.0,117.4", max_pages: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.bounds = _parse_bounds(bounds)
        self.max_pages = int(max_pages)
        self.table_name = "spatial_poi"
        self.ak = project_settings.api_keys.baidu_map
        if not self.ak:
            self.logger.warning("BAIDU_LBS_AK not configured; requests may fail.")

    def start_requests(self):
        for page in range(self.max_pages):
            params = {
                "query": self.category,
                "bounds": f"{self.bounds[0]}|{self.bounds[1]}",
                "output": "json",
                "page_size": 20,
                "page_num": page,
                "ak": self.ak or "",
            }
            url = f"{BAIDU_POI_URL}?{urlencode(params)}"
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        payload = json.loads(response.text)
        for poi in payload.get("results", []):
            location = poi.get("location", {})
            yield PoiItem(
                name=poi.get("name"),
                category=self.category,
                latitude=location.get("lat"),
                longitude=location.get("lng"),
                address=poi.get("address"),
            )
