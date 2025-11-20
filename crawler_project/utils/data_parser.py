"""Text parsing helpers for extracting disaster metadata from articles."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Optional

DISASTER_KEYWORDS = {
    "地震": ["地震", "震感", "震源"],
    "火灾": ["火灾", "起火", "燃烧"],
    "事故": ["事故", "碰撞", "塌陷", "爆炸"],
    "洪涝": ["洪水", "积水", "暴雨"],
}

LOSS_PATTERN = re.compile(r"(?P<amount>\d+(?:\.\d+)?)\s*(人|万元|亿元)")
DATE_PATTERN = re.compile(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})")


def detect_disaster_type(text: str) -> Optional[str]:
    text = text or ""
    for disaster, keywords in DISASTER_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return disaster
    return None


def extract_loss_info(text: str) -> Optional[Dict[str, str]]:
    match = LOSS_PATTERN.search(text or "")
    if not match:
        return None
    return {"amount": match.group("amount"), "unit": match.group(2)}


def parse_date(text: str) -> Optional[datetime]:
    if not text:
        return None
    match = DATE_PATTERN.search(text)
    if not match:
        return None
    year, month, day = map(int, match.groups())
    return datetime(year, month, day)
