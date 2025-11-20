"""Headless browser helper built on Selenium."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver(driver_path: Optional[str] = None) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    if driver_path:
        driver.service.path = driver_path
    return driver


@contextmanager
def headless_browser(driver_path: Optional[str] = None) -> Iterator[webdriver.Chrome]:
    driver = create_driver(driver_path)
    try:
        yield driver
    finally:
        driver.quit()


def fetch_dynamic_html(url: str, wait: float = 2.0) -> str:
    with headless_browser() as driver:
        driver.get(url)
        time.sleep(wait)
        return driver.page_source
