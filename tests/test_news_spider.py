from __future__ import annotations

from datetime import datetime

from scrapy.http import HtmlResponse

from crawler_project.scrapy_app.spiders.news_spider import NorthNewsSpider


def test_news_spider_parse_detail_extracts_fields():
    spider = NorthNewsSpider()
    html = (
        "<html><body><div class='article'>"
        "2019年5月1日凌晨，北京某区发生火灾，造成20人受伤。</div></body></html>"
    )
    response = HtmlResponse(url="http://test/detail", body=html, encoding="utf-8")

    items = list(spider.parse_detail(response, title="测试火灾", publish_date=datetime(2019, 5, 1)))

    assert len(items) == 1
    item = items[0]
    assert item["disaster_type"] == "火灾"
    assert item["loss"]["amount"] == "20"
    assert item["publish_date"] == "2019-05-01T00:00:00"
