"""Abstract base crawler with retry, throttle, and logging."""

from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional

import aiohttp
import json
import tenacity

from ..config import settings
from ..utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)


def _sleep_interval() -> float:
    policy = settings.request_policy
    return random.uniform(policy.min_delay_seconds, policy.max_delay_seconds)


class BaseCrawler(ABC):
    """Shared features for all crawlers."""

    name: str = "base"

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.session = session
        self.proxy_manager = ProxyManager(settings.proxy.pool_file)
        self.user_agents = settings.user_agents.desktop

    async def __aenter__(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=settings.request_policy.timeout_seconds)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def fetch_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> dict:
        response_text = await self._request("GET", url, params=params)
        return json.loads(response_text)

    async def fetch_text(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        return await self._request("GET", url, params=params)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(settings.request_policy.max_retries),
        wait=tenacity.wait_exponential(multiplier=settings.request_policy.backoff_factor),
        reraise=True,
    )
    async def _request(self, method: str, url: str, **kwargs) -> str:
        if not self.session:
            raise RuntimeError("ClientSession not initialized. Use async context manager.")

        proxy = self.proxy_manager.next_proxy() if settings.proxy.enabled else None
        if proxy:
            kwargs.setdefault("proxy", proxy)

        headers = {"User-Agent": random.choice(self.user_agents)}
        async with self.session.request(method, url, headers=headers, **kwargs) as resp:
            resp.raise_for_status()
            text = await resp.text()
            await asyncio.sleep(_sleep_interval())
            return text

    @abstractmethod
    async def crawl(self, **kwargs) -> Iterable[dict]:
        raise NotImplementedError
