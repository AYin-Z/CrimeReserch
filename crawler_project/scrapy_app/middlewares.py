from __future__ import annotations

import random

from crawler_project.config import settings as project_settings


class ConfigUserAgentMiddleware:
    """Rotate user agents from project config."""

    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(project_settings.user_agents.desktop)

    def process_request(self, request, spider):
        request.headers.setdefault("User-Agent", random.choice(self.user_agents))
        return None
