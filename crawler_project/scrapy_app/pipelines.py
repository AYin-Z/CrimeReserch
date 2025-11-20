from __future__ import annotations

import logging
from collections import defaultdict
from typing import Dict, List

import pandas as pd

from crawler_project.utils.storage_handler import StorageHandler

logger = logging.getLogger(__name__)


class PostgresPipeline:
    """Batch items and persist via StorageHandler."""

    def __init__(self, batch_size: int = 100) -> None:
        self.batch_size = batch_size
        self.storage: StorageHandler | None = None
        self._buffers: Dict[str, List[dict]] = defaultdict(list)

    @classmethod
    def from_crawler(cls, crawler):
        batch_size = crawler.settings.getint("PIPELINE_BATCH_SIZE", 100)
        return cls(batch_size=batch_size)

    def open_spider(self, spider):
        self.storage = StorageHandler()
        logger.info("Opened Postgres pipeline for spider %s", spider.name)

    def close_spider(self, spider):
        self._flush_all(spider)
        logger.info("Closed Postgres pipeline for spider %s", spider.name)

    def process_item(self, item, spider):
        table = getattr(spider, "table_name", f"{spider.name}_records")
        data = dict(item)
        self._buffers[table].append(data)
        if len(self._buffers[table]) >= self.batch_size:
            self._flush_table(table)
        return item

    def _flush_table(self, table: str):
        buffer = self._buffers.get(table)
        if not buffer:
            return
        assert self.storage is not None
        df = pd.DataFrame(buffer)
        if df.empty:
            return
        self.storage.save_dataframe(df, table)
        logger.info("Inserted %s rows into %s", len(df), table)
        self._buffers[table].clear()

    def _flush_all(self, spider):
        for table in list(self._buffers.keys()):
            self._flush_table(table)
