from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from crawler_project.scrapy_app import pipelines
from crawler_project.scrapy_app.pipelines import PostgresPipeline


class DummyStorage:
    def __init__(self):
        self.saved = []

    def save_dataframe(self, df: pd.DataFrame, table: str, if_exists: str = "append") -> None:
        self.saved.append((table, df.copy()))


def test_postgres_pipeline_flush(monkeypatch):
    dummy = DummyStorage()
    monkeypatch.setattr(pipelines, "StorageHandler", lambda: dummy)

    pipeline = PostgresPipeline(batch_size=2)
    spider = SimpleNamespace(name="dummy", table_name="dummy_table")
    pipeline.open_spider(spider)

    pipeline.process_item({"a": 1}, spider)
    pipeline.process_item({"a": 2}, spider)

    assert len(dummy.saved) == 1
    table, df = dummy.saved[0]
    assert table == "dummy_table"
    assert df.shape[0] == 2

    pipeline.close_spider(spider)


@pytest.mark.parametrize("items", [[{"x": 1}], []])
def test_postgres_pipeline_handles_small_batches(monkeypatch, items):
    dummy = DummyStorage()
    monkeypatch.setattr(pipelines, "StorageHandler", lambda: dummy)
    pipeline = PostgresPipeline(batch_size=10)
    spider = SimpleNamespace(name="dummy")
    pipeline.open_spider(spider)

    for item in items:
        pipeline.process_item(item, spider)

    pipeline.close_spider(spider)

    if items:
        assert dummy.saved, "Items should flush on close"
    else:
        assert not dummy.saved
