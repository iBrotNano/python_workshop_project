import sqlite3
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlite_rag import SQLiteRag
from sqlite_rag.settings import Settings
from config.configuration import Configuration, configuration
from persistence.database_engine import DatabaseEngine
from persistence.database_maintenance import DatabaseMaintenance
from persistence.retriever import Retriever
from persistence.retriever_manager import RetrieverManager
from persistence.sqlite_rag_factory import SQLiteRagFactory


def test_sqlite_rag_factory_opens_existing_database(monkeypatch):
    calls = []
    rag = object()
    configuration = SimpleNamespace(sqlite_file_path="nutrition.db")

    monkeypatch.setattr(
        "persistence.sqlite_rag_factory.SQLiteRag.create",
        lambda path, **kwargs: calls.append((path, kwargs)) or rag,
    )

    result = SQLiteRagFactory(configuration).create_for_retrieval()
    assert result is rag
    assert calls == [("nutrition.db", {"require_existing": True})]


def test_sqlite_rag_factory_configures_embedding_database(monkeypatch):
    calls = []
    rag = object()

    configuration = SimpleNamespace(
        sqlite_file_path="nutrition.db",
        ai_use_vulcan_llama_backend=False,
        ai_used_embedding_model_path="model.gguf",
        ai_embedding_chunk_size=2024,
        ai_embedding_chunk_overlap=256,
    )

    monkeypatch.setattr(
        "persistence.sqlite_rag_factory.SQLiteRag.create",
        lambda path, **kwargs: calls.append((path, kwargs)) or rag,
    )

    result = SQLiteRagFactory(configuration).create_for_embedding(quantize_scan=True)

    assert result is rag
    assert Settings.use_gpu is False

    assert calls == [
        (
            "nutrition.db",
            {
                "settings": {
                    "model_path": "model.gguf",
                    "chunk_size": 2024,
                    "chunk_overlap": 256,
                    "quantize_scan": True,
                }
            },
        )
    ]


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

    with Retriever(
        SimpleNamespace(
            sqlite_file_path=database_path,
            experimental_batched_sentence_scoring=True,
        )
    ) as retriever:
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


def test_updater_creates_missing_rag_database_that_retriever_can_open(
    tmp_path, monkeypatch
):
    from persistence.nutrition_db_updater import NutritionDbUpdater

    model_path = Path(configuration.ai_used_embedding_model_path)

    if not model_path.is_file():
        pytest.skip("The configured embedding model is not available.")

    monkeypatch.setattr(Settings, "use_gpu", False)
    config = Configuration()
    config.sqlite_file_path = str(tmp_path / "nutrition.db")
    config.ai_use_vulcan_llama_backend = False

    engine = create_engine(f"sqlite:///{Path(config.sqlite_file_path).as_posix()}")

    database_engine = DatabaseEngine(
        engine,
        sessionmaker(bind=engine),
        declarative_base(),
    )

    updater = NutritionDbUpdater(config, database_engine)
    rag = updater._NutritionDbUpdater__create_clean_rag(quantize_scan=False)

    try:
        assert Path(config.sqlite_file_path).is_file()

        with sqlite3.connect(config.sqlite_file_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }

        assert "documents" in tables
    finally:
        rag.close()
        engine.dispose()

    with Retriever(config) as retriever:
        assert retriever.rag is not None


def test_unsupported_sqlite_rag_version_uses_library_search(monkeypatch):
    calls = []
    rag = SimpleNamespace(
        search=lambda query, top_k: calls.append((query, top_k)) or [],
        close=lambda: calls.append("close"),
    )
    monkeypatch.setattr(
        "persistence.retriever.SQLiteRag.create", lambda *args, **kwargs: rag
    )
    monkeypatch.setattr("persistence.retriever.version", lambda name: "0.2.0")
    retriever = Retriever(
        SimpleNamespace(
            sqlite_file_path="database.db",
            experimental_batched_sentence_scoring=True,
        )
    )

    assert retriever.retrieve("apple", 2) == []
    retriever.close()
    retriever.close()
    with pytest.raises(RuntimeError, match="closed"):
        retriever.retrieve("apple")

    assert calls == [("apple", 2), "close"]


def test_experimental_batched_sentence_scoring_uses_normal_search_when_disabled(
    monkeypatch,
):
    calls = []
    rag = SimpleNamespace(
        search=lambda query, top_k: calls.append((query, top_k)) or [],
        close=lambda: None,
    )
    monkeypatch.setattr(
        "persistence.retriever.SQLiteRag.create", lambda *args, **kwargs: rag
    )
    monkeypatch.setattr("persistence.retriever.version", lambda name: "0.1.4")
    retriever = Retriever(
        SimpleNamespace(
            sqlite_file_path="database.db",
            experimental_batched_sentence_scoring=False,
        )
    )

    assert retriever.retrieve("apple", 2) == []
    assert calls == [("apple", 2)]


def test_experimental_batched_sentence_scoring_uses_helper_when_enabled(monkeypatch):
    expected = [object()]
    rag = SimpleNamespace(
        _settings=SimpleNamespace(top_k_sentences=5),
        close=lambda: None,
    )
    monkeypatch.setattr(
        "persistence.retriever.SQLiteRag.create", lambda *args, **kwargs: rag
    )
    monkeypatch.setattr("persistence.retriever.version", lambda name: "0.1.4")
    monkeypatch.setattr(
        Retriever,
        "_Retriever__search_with_batched_sentence_scoring",
        lambda self, rag, query, top_k: expected,
    )
    retriever = Retriever(
        SimpleNamespace(
            sqlite_file_path="database.db",
            experimental_batched_sentence_scoring=True,
        )
    )

    assert retriever.retrieve("apple", 2) is expected
