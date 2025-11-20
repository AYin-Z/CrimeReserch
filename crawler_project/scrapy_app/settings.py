"""Scrapy settings bridging crawler_project config."""

from __future__ import annotations

from crawler_project import config as project_config

POLICY = project_config.settings.request_policy

BOT_NAME = "crawler_project"
SPIDER_MODULES = ["crawler_project.scrapy_app.spiders"]
NEWSPIDER_MODULE = "crawler_project.scrapy_app.spiders"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = POLICY.min_delay_seconds
CONCURRENT_REQUESTS_PER_DOMAIN = 8
RETRY_ENABLED = True
RETRY_TIMES = POLICY.max_retries

COOKIES_ENABLED = False
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

ITEM_PIPELINES = {
    "crawler_project.scrapy_app.pipelines.PostgresPipeline": 300,
}

DOWNLOADER_MIDDLEWARES = {
    "crawler_project.scrapy_app.middlewares.ConfigUserAgentMiddleware": 400,
}

TELNETCONSOLE_ENABLED = False
LOG_STDOUT = False
LOG_LEVEL = "INFO"

PIPELINE_BATCH_SIZE = 200

# Ensure new features stay compatible
twisted_timeout = POLICY.timeout_seconds
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
