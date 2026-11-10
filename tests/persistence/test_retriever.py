from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlite_rag import SQLiteRag
from sqlite_rag.settings import Settings
from sqlalchemy import create_engine

from config.configuration import configuration
from persistence.database_maintenance import DatabaseMaintenance
from persistence.retriever import Retriever
from persistence.retriever_manager import RetrieverManager


@pytest.mark.parametrize("quantized", [False, True])
def test_batched_search_matches_sqlite_rag_results(tmp_path, monkeypatch, quantized):
    model_path = Path(configuration.ai_used_embedding_model_path)
    if not model_path.is_file():
        pytest.skip("The configured embedding model is not available.")
    monkeypatch.setattr(Settings, "use_gpu", False)
    database_path = str(tmp_path / "vectors.db")
    rag = SQLiteRag.create(
        database_path,
        settings={
            "model_path": str(model_path),
            "chunk_size": 256,
            "chunk_overlap": 0,
            "quantize_scan": False,
        },
    )
    try:
        rag.add_text("Apple juice. Apple juice. Sweet fruit with vitamins.", uri="one")
        rag.add_text("Milk has protein. Dairy is nutritious.", uri="two")
        rag.add_text("Apple yoghurt. Milk with fruit.", uri="three")
        if quantized:
            rag.quantize_vectors()
    finally:
        rag.close()

    reference = SQLiteRag.create(database_path, settings={"quantize_scan": quantized})
    try:
        expected = [asdict(item) for item in reference.search("apple", top_k=2)]
    finally:
        reference.close()

    engine = create_engine(f"sqlite:///{Path(database_path).as_posix()}")
    try:
        DatabaseMaintenance(engine).compact()
    finally:
        engine.dispose()

    with Retriever(SimpleNamespace(sqlite_file_path=database_path)) as retriever:
        actual = [asdict(item) for item in retriever.retrieve("apple", top_k=2)]
        repeated = [asdict(item) for item in retriever.retrieve("apple", top_k=2)]

    assert actual == expected
    assert repeated == expected


def test_retriever_manager_reuses_and_closes_instance(monkeypatch):
    created = []

    class FakeRetriever:
        def __init__(self, config):
            self.closed = False
            created.append(self)

        def close(self):
            self.closed = True

    monkeypatch.setattr("persistence.retriever_manager.Retriever", FakeRetriever)
    manager = RetrieverManager()
    config = SimpleNamespace(sqlite_file_path="database.db")

    first = manager.get(config)
    assert manager.get(config) is first
    manager.close()
    assert first.closed
    second = manager.get(config)
    assert second is not first
    manager.close()
    assert second.closed


def test_retriever_manager_closes_previous_database_on_path_change(monkeypatch):
    class FakeRetriever:
        def __init__(self, config):
            self.closed = False

        def close(self):
            self.closed = True

    monkeypatch.setattr("persistence.retriever_manager.Retriever", FakeRetriever)
    manager = RetrieverManager()
    first = manager.get(SimpleNamespace(sqlite_file_path="first.db"))
    second = manager.get(SimpleNamespace(sqlite_file_path="second.db"))

    assert first.closed
    assert second is not first
    manager.close()


def test_updater_invalidates_cached_retriever_before_modifying_database(monkeypatch):
    from persistence.nutrition_db_updater import NutritionDbUpdater

    events = []
    monkeypatch.setattr(
        "persistence.nutrition_db_updater.retriever_manager",
        SimpleNamespace(close=lambda: events.append("close")),
    )
    updater = NutritionDbUpdater(
        SimpleNamespace(
            temp_folder=".",
            openfoodfacts_gz_file_name="data.csv.gz",
            openfoodfacts_download_url="https://example.invalid/data.csv.gz",
        ),
        SimpleNamespace(),
    )
    updater._NutritionDbUpdater__openfoodfacts_pipeline = SimpleNamespace(
        run=lambda callback: events.append("update")
    )

    updater.update(skip_embedding_creation=True)

    assert events == ["close", "update"]


def test_unsupported_sqlite_rag_version_uses_library_search(monkeypatch):
    calls = []
    rag = SimpleNamespace(
        search=lambda query, top_k: calls.append((query, top_k)) or [],
        close=lambda: calls.append("close"),
    )
    monkeypatch.setattr("persistence.retriever.SQLiteRag.create", lambda *args, **kwargs: rag)
    monkeypatch.setattr("persistence.retriever.version", lambda name: "0.2.0")
    retriever = Retriever(SimpleNamespace(sqlite_file_path="database.db"))

    assert retriever.retrieve("apple", 2) == []
    retriever.close()
    retriever.close()
    with pytest.raises(RuntimeError, match="closed"):
        retriever.retrieve("apple")

    assert calls == [("apple", 2), "close"]
