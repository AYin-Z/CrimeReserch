"""Spatial data acquisition via Baidu LBS and OpenStreetMap."""

from __future__ import annotations

import json
from typing import AsyncGenerator, Dict, Iterable, List

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from ..config import settings
from .base_crawler import BaseCrawler

BAIDU_POI_URL = "http://api.map.baidu.com/place/v2/search"


class SpatialCrawler(BaseCrawler):
    name = "spatial"

    async def crawl(self, bounds: Dict[str, float], category: str) -> AsyncGenerator[dict, None]:
        params = {
            "query": category,
            "bounds": f"{bounds['southwest']},{bounds['northeast']}",
            "output": "json",
            "ak": settings.api_keys.baidu_map,
        }
        response = await self.fetch_text(BAIDU_POI_URL, params=params)
        payload = json.loads(response)
        for poi in payload.get("results", []):
            coordinate = self._to_wgs84(poi["location"]["lng"], poi["location"]["lat"])
            yield {
                "name": poi["name"],
                "category": category,
                "longitude": coordinate[0],
                "latitude": coordinate[1],
                "address": poi.get("address"),
            }

    def _to_wgs84(self, lng: float, lat: float):
        # Placeholder for real conversion logic
        return lng, lat

    def to_geodataframe(self, records: Iterable[dict]) -> gpd.GeoDataFrame:
        df = pd.DataFrame(records)
        geometry = [Point(lon, lat) for lon, lat in zip(df["longitude"], df["latitude"])]
        return gpd.GeoDataFrame(df, geometry=geometry, crs=f"EPSG:{settings.grid.srid}")
