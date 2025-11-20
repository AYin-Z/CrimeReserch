from __future__ import annotations

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    publish_date = scrapy.Field()
    disaster_type = scrapy.Field()
    location = scrapy.Field()
    loss = scrapy.Field()
    content = scrapy.Field()


class HousingItem(scrapy.Item):
    community = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()
    unit_price = scrapy.Field()
    area = scrapy.Field()
    deal_date = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()


class LegalItem(scrapy.Item):
    title = scrapy.Field()
    judgment_date = scrapy.Field()
    case_type = scrapy.Field()
    location = scrapy.Field()
    charges = scrapy.Field()
    law_articles = scrapy.Field()
    url = scrapy.Field()


class PoiItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    address = scrapy.Field()
