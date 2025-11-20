"""Proxy pool management with health tracking."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Iterator, List, Optional


class ProxyManager:
    """Simple rotating proxy pool with failure backoff."""

    def __init__(self, proxy_file: Optional[Path] = None) -> None:
        self.proxy_file = proxy_file
        self._proxies: List[str] = []
        self._blocked: dict[str, float] = {}
        if proxy_file and proxy_file.exists():
            self._proxies = [p.strip() for p in proxy_file.read_text().splitlines() if p.strip()]

    def __iter__(self) -> Iterator[str]:
        while True:
            yield self.next_proxy()

    def next_proxy(self) -> Optional[str]:
        if not self._proxies:
            return None
        available = [p for p in self._proxies if self._blocked.get(p, 0) < time.time()]
        if not available:
            return None
        return random.choice(available)

    def mark_failure(self, proxy: str, cooldown: int = 300) -> None:
        self._blocked[proxy] = time.time() + cooldown

    def add_proxy(self, proxy: str) -> None:
        if proxy not in self._proxies:
            self._proxies.append(proxy)
