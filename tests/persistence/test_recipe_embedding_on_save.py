import logging
import sqlite3
import pytest

from contextlib import nullcontext
from copy import copy
from pathlib import Path
from types import SimpleNamespace
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from persistence.database_engine import DatabaseEngine
from persistence.database_engine_factory import database_engine
from persistence.db_schema_registry import load_db_schema_definitions
from persistence.unit_of_work import UnitOfWork
from config.configuration import configuration
from recipes.recipe import Recipe
from recipes.recipe_entity import RecipeEntity


@pytest.fixture
def recipe_database(tmp_path, monkeypatch):
    load_db_schema_definitions()
    engine = create_engine(f"sqlite:///{(tmp_path / 'recipes.db').as_posix()}")
    database_engine.Base.metadata.create_all(engine)

    test_database = DatabaseEngine(
        engine, sessionmaker(bind=engine), database_engine.Base
    )

    monkeypatch.setattr("persistence.unit_of_work.database_engine", test_database)
    yield test_database
    engine.dispose()


def test_committed_new_recipes_are_indexed_once_after_commit(
    recipe_database, monkeypatch
):
    indexed = []

    def create_embedding(indexer, recipe_id, recipe):
        with recipe_database.get_db() as session:
            stored = session.get(RecipeEntity, recipe_id)
            assert stored is not None
            assert stored.name == recipe.name

        indexed.append((recipe_id, recipe.name))

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeEmbeddingIndexer.create_embedding",
        create_embedding,
        raising=False,
    )

    with UnitOfWork() as uow:
        assert uow.recipes.try_add(Recipe(name="First"))
        assert uow.recipes.try_add(Recipe(name="Second"))
        assert indexed == []
        assert uow.commit() == []
        assert uow.commit() == []

    assert indexed == [(1, "First"), (2, "Second")]


def test_rolled_back_recipe_and_duplicate_are_not_indexed(recipe_database, monkeypatch):
    indexed = []

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeEmbeddingIndexer.create_embedding",
        lambda indexer, recipe_id, recipe: indexed.append(recipe_id),
        raising=False,
    )

    with UnitOfWork() as uow:
        assert uow.recipes.try_add(Recipe(name="Existing"))
        uow.commit()

    with UnitOfWork() as uow:
        assert not uow.recipes.try_add(Recipe(name="Existing"))
        uow.commit()

    with pytest.raises(RuntimeError, match="abort"):
        with UnitOfWork() as uow:
            assert uow.recipes.try_add(Recipe(name="Rolled back"))
            raise RuntimeError("abort")

    assert indexed == [1]


def test_failed_recipe_commit_never_creates_embedding(recipe_database, monkeypatch):
    indexed = []

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeEmbeddingIndexer.create_embedding",
        lambda indexer, recipe_id, recipe: indexed.append(recipe_id),
        raising=False,
    )

    with UnitOfWork() as uow:
        assert uow.recipes.try_add(Recipe(name="Not committed"))

        monkeypatch.setattr(
            uow._session,
            "commit",
            lambda: (_ for _ in ()).throw(RuntimeError("commit failed")),
        )

        with pytest.raises(RuntimeError, match="commit failed"):
            uow.commit()

    assert indexed == []

    with recipe_database.get_db() as session:
        assert session.query(RecipeEntity).count() == 0


def test_embedding_failure_keeps_recipe_and_attempts_other_recipes(
    recipe_database, monkeypatch, caplog
):
    attempted = []

    def create_embedding(indexer, recipe_id, recipe):
        attempted.append(recipe.name)

        if recipe.name == "First":
            raise RuntimeError("embedding failed")

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeEmbeddingIndexer.create_embedding",
        create_embedding,
        raising=False,
    )

    with caplog.at_level(logging.ERROR), UnitOfWork() as uow:
        assert uow.recipes.try_add(Recipe(name="First"))
        assert uow.recipes.try_add(Recipe(name="Second"))
        assert uow.commit() == [1]

    with recipe_database.get_db() as session:
        assert session.query(RecipeEntity).count() == 2

    assert attempted == ["First", "Second"]
    assert "embedding failed" in caplog.text


def test_single_recipe_failure_rolls_back_partial_document(monkeypatch, tmp_path):
    from persistence.recipe_embedding_indexer import RecipeEmbeddingIndexer

    connection = sqlite3.connect(tmp_path / "sidecar.db")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE documents (uri TEXT, content TEXT)")
    connection.execute("INSERT INTO documents VALUES ('recipe:1', 'unchanged')")
    connection.commit()

    class FailingRag:
        _conn = connection

        def add_text(self, content, uri, metadata):
            connection.execute("INSERT INTO documents VALUES (?, ?)", (uri, content))
            raise RuntimeError("insertion failed")

        def close(self):
            pass

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.SQLiteRagFactory.create_for_recipe_embedding",
        lambda factory: FailingRag(),
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda *args: None,
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.retriever_manager",
        SimpleNamespace(close=lambda: None),
    )

    config = SimpleNamespace(
        ai_used_embedding_model={"repo": "model", "filename": "model.gguf"}
    )

    with pytest.raises(RuntimeError, match="insertion failed"):
        RecipeEmbeddingIndexer(config, SimpleNamespace()).create_embedding(
            2, Recipe(name="New")
        )

    assert [tuple(row) for row in connection.execute("SELECT * FROM documents")] == [
        ("recipe:1", "unchanged")
    ]

    connection.close()


def test_existing_recipe_uri_is_not_overwritten(monkeypatch, tmp_path):
    from persistence.recipe_embedding_indexer import RecipeEmbeddingIndexer

    connection = sqlite3.connect(tmp_path / "sidecar.db")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE documents (uri TEXT, content TEXT)")
    connection.execute("INSERT INTO documents VALUES ('recipe:1', 'unchanged')")
    connection.commit()
    rag = SimpleNamespace(_conn=connection, close=lambda: None)

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.SQLiteRagFactory.create_for_recipe_embedding",
        lambda factory: rag,
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.retriever_manager",
        SimpleNamespace(close=lambda: None),
    )

    with pytest.raises(ValueError, match="already exists"):
        RecipeEmbeddingIndexer(SimpleNamespace(), SimpleNamespace()).create_embedding(
            1, Recipe(name="New")
        )

    assert tuple(connection.execute("SELECT * FROM documents").fetchone()) == (
        "recipe:1",
        "unchanged",
    )

    connection.close()


def test_real_sidecar_rolls_back_document_when_chunk_insert_fails(
    monkeypatch, tmp_path
):
    from sqlite_rag import SQLiteRag
    from sqlite_rag.models.chunk import Chunk
    from persistence.recipe_embedding_indexer import RecipeEmbeddingIndexer

    rag = SQLiteRag.create(
        str(tmp_path / "sidecar.db"), settings={"quantize_scan": False}
    )

    rag._conn.execute(
        "CREATE TRIGGER fail_chunk BEFORE INSERT ON chunks "
        "BEGIN SELECT RAISE(ABORT, 'chunk failure'); END"
    )

    rag._conn.commit()
    monkeypatch.setattr(rag, "_ensure_initialized", lambda: None)
    monkeypatch.setattr(rag._engine, "create_new_context", lambda: None)
    monkeypatch.setattr(rag._engine, "free_context", lambda: None)

    def process(document):
        document.chunks = [Chunk(content="chunk", embedding=b"vector")]
        return document

    monkeypatch.setattr(rag._engine, "process", process)
    monkeypatch.setattr(rag, "close", lambda: None)

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.SQLiteRagFactory.create_for_recipe_embedding",
        lambda factory: rag,
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda *args: None,
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.retriever_manager",
        SimpleNamespace(close=lambda: None),
    )

    config = SimpleNamespace(
        ai_used_embedding_model={"repo": "model", "filename": "model.gguf"}
    )

    try:
        with pytest.raises(sqlite3.IntegrityError, match="chunk failure"):
            RecipeEmbeddingIndexer(config, SimpleNamespace()).create_embedding(
                2, Recipe(name="New")
            )

        assert rag._conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
        assert rag._conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 0
        rag._conn.execute("DROP TRIGGER fail_chunk")
        rag._conn.commit()

        monkeypatch.setattr(
            "persistence.recipe_embedding_indexer.RecipeRepository",
            lambda session: SimpleNamespace(
                get_all_with_ids=lambda: [(2, Recipe(name="New"))]
            ),
        )

        indexer = RecipeEmbeddingIndexer(
            config, SimpleNamespace(get_db=lambda: nullcontext(object()))
        )

        assert indexer.create_embeddings() == {"created": 1, "skipped": 0}

        assert (
            rag._conn.execute("SELECT uri FROM documents").fetchone()[0] == "recipe:2"
        )
    finally:
        rag._conn.close()


def test_real_sidecar_preserves_existing_vectors_and_ranks_new_recipe(
    recipe_database, monkeypatch, tmp_path
):
    from persistence.retriever import Retriever
    from persistence.sqlite_rag_factory import SQLiteRagFactory

    if not Path(configuration.ai_used_embedding_model_path).is_file():
        pytest.skip("The configured embedding model is not available.")

    config = copy(configuration)
    config.sqlite_file_path = str(tmp_path / "nutrition.db")
    config.ai_use_vulcan_llama_backend = False
    config.experimental_batched_sentence_scoring = False
    monkeypatch.setattr("persistence.unit_of_work.configuration", config)

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda *args: None,
    )
    sidecar = SQLiteRagFactory(config).recipe_database_path

    with UnitOfWork() as uow:
        assert uow.recipes.try_add(
            Recipe(name="Roast beef dinner", instructions="Cook beef with potatoes.")
        )

        assert uow.commit() == []

    with sqlite3.connect(sidecar) as connection:
        existing_document = connection.execute(
            "SELECT id, content, uri, metadata FROM documents WHERE uri = 'recipe:1'"
        ).fetchone()

        existing_chunks = connection.execute(
            "SELECT id, content, embedding FROM chunks WHERE document_id = ?",
            (existing_document[0],),
        ).fetchall()

        existing_sentences = connection.execute(
            "SELECT s.id, s.embedding FROM sentences s "
            "JOIN chunks c ON c.id = s.chunk_id WHERE c.document_id = ?",
            (existing_document[0],),
        ).fetchall()

    assert existing_chunks
    assert all(chunk[2] for chunk in existing_chunks)

    with UnitOfWork() as uow:
        assert uow.recipes.try_add(
            Recipe(
                name="Apple cinnamon oatmeal",
                instructions="Cook oats with apples, cinnamon, and sweet fruit.",
            )
        )

        assert uow.commit() == []

    with sqlite3.connect(sidecar) as connection:
        assert (
            connection.execute(
                "SELECT id, content, uri, metadata FROM documents WHERE uri = 'recipe:1'"
            ).fetchone()
            == existing_document
        )

        assert (
            connection.execute(
                "SELECT id, content, embedding FROM chunks WHERE document_id = ?",
                (existing_document[0],),
            ).fetchall()
            == existing_chunks
        )

        assert (
            connection.execute(
                "SELECT s.id, s.embedding FROM sentences s "
                "JOIN chunks c ON c.id = s.chunk_id WHERE c.document_id = ?",
                (existing_document[0],),
            ).fetchall()
            == existing_sentences
        )

        document = connection.execute(
            "SELECT id, metadata FROM documents WHERE uri = 'recipe:2'"
        ).fetchone()

        assert document is not None
        assert '"recipe_id": 2' in document[1]

        assert (
            connection.execute(
                "SELECT count(*) FROM chunks WHERE document_id = ? AND length(embedding) > 0",
                (document[0],),
            ).fetchone()[0]
            > 0
        )

    with Retriever(config, sidecar) as retriever:
        results = retriever.retrieve("apple cinnamon oatmeal fruit", top_k=2)

    assert len(results) == 2
    assert results[0].document.metadata["recipe_id"] == 2
    assert results[0].vec_rank == 1
    first_distance = results[0].vec_distance
    second_distance = results[1].vec_distance
    assert first_distance is not None
    assert second_distance is not None
    assert first_distance < second_distance
