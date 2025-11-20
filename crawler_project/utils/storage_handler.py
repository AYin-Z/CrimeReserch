"""Database and file persistence utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ..config import settings


class StorageHandler:
    """Handles writing tabular and spatial data to disk and PostgreSQL."""

    _ENGINE_CACHE: Dict[str, Engine] = {}

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or settings.storage.postgres_dsn
        self.engine = self._get_engine(self.dsn)
        settings.storage.raw_html_dir.mkdir(parents=True, exist_ok=True)
        settings.storage.geojson_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _get_engine(cls, dsn: str) -> Engine:
        if dsn not in cls._ENGINE_CACHE:
            storage_cfg = settings.storage
            cls._ENGINE_CACHE[dsn] = create_engine(
                dsn,
                pool_pre_ping=True,
                pool_size=storage_cfg.pool_size,
                max_overflow=storage_cfg.max_overflow,
                pool_timeout=storage_cfg.pool_timeout,
            )
        return cls._ENGINE_CACHE[dsn]

    def save_dataframe(self, df: pd.DataFrame, table: str, if_exists: str = "append") -> None:
        df.to_sql(table, self.engine, if_exists=if_exists, index=False)

    def save_geojson(self, gdf: gpd.GeoDataFrame, name: str) -> Path:
        target = settings.storage.geojson_dir / f"{name}.geojson"
        gdf.to_file(target, driver="GeoJSON")
        return target

    def save_html(self, html: str, identifier: str) -> Path:
        target = settings.storage.raw_html_dir / f"{identifier}.html"
        target.write_text(html, encoding="utf-8")
        return target

    def export_records(self, records: Iterable[dict], path: Path) -> Path:
        data: List[dict] = list(records)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_connection(self) -> bool:
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
