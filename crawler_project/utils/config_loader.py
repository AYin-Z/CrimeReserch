"""Utility helpers for loading crawler configuration from YAML/JSON files."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml

from .. import config


def load_config_file(path: Path | str | None = None) -> Dict[str, Any]:
    """Load configuration overrides from YAML/JSON, returning a dict."""

    target = Path(path) if path else config.DEFAULT_CONFIG_FILE
    if not target.exists():
        return {}

    if target.suffix.lower() in {".yml", ".yaml"}:
        return yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if target.suffix.lower() == ".json":
        return json.loads(target.read_text(encoding="utf-8"))

    raise ValueError(f"Unsupported config format: {target.suffix}")


def apply_overrides(overrides: Dict[str, Any]) -> config.ProjectSettings:
    """Apply nested dict overrides onto the global settings dataclasses."""

    def _apply(target, data):
        for key, value in data.items():
            if not hasattr(target, key):
                continue
            current = getattr(target, key)
            if isinstance(value, dict) and not isinstance(current, (str, int, float)):
                _apply(current, value)
            else:
                setattr(target, key, value)

    cloned = config.ProjectSettings()
    _apply(cloned, overrides)
    return cloned


def load_settings(path: Path | str | None = None) -> config.ProjectSettings:
    """Load settings merging file overrides with environment variables."""

    overrides = load_config_file(path)
    env_overrides = _load_env_overrides()

    merged = {**overrides, **env_overrides}
    applied = apply_overrides(merged)
    config.settings = applied
    return applied


def _load_env_overrides() -> Dict[str, Any]:
    """Map environment variables to nested config overrides."""

    mapping: Dict[str, Any] = {}
    if api_key := os.getenv("BAIDU_LBS_AK"):
        mapping.setdefault("api_keys", {})["baidu_map"] = api_key
    if pg_dsn := os.getenv("POSTGRES_DSN"):
        mapping.setdefault("storage", {})["postgres_dsn"] = pg_dsn
    return mapping
