import sqlite3
import pytest

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from copy import copy
from threading import Event
from types import SimpleNamespace
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlite_rag import SQLiteRag
from sqlite_rag.models.chunk import Chunk
from sqlite_rag.models.document import Document
from sqlite_rag.models.sentence import Sentence
from config.configuration import configuration
from persistence.database_engine import DatabaseEngine
from persistence.database_engine_factory import database_engine
from recipes.recipe_embedding_cleanup import RecipeEmbeddingCleanup
from recipes.recipe_embedding_indexer import RecipeEmbeddingIndexer
from persistence.unit_of_work import UnitOfWork
from recipes.recipe import Recipe
from recipes.recipe_entity import RecipeEntity

CREATE_EMBEDDING = RecipeEmbeddingIndexer.create_embedding


@pytest.fixture
def databases(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'main.db').as_posix()}")
    db = DatabaseEngine(engine, sessionmaker(bind=engine), database_engine.Base)
    db.initialize_schema()
    config = copy(configuration)
    config.sqlite_file_path = str(tmp_path / "main.db")
    config.ai_use_vulcan_llama_backend = False
    monkeypatch.setattr("persistence.unit_of_work.database_engine", db)
    monkeypatch.setattr("persistence.unit_of_work.configuration", config)

    monkeypatch.setattr(
        "recipes.recipe_embedding_indexer.RecipeEmbeddingIndexer.create_embedding",
        lambda *args: None,
    )

    yield db, config, tmp_path / "main_recipes.db"
    engine.dispose()


def add_recipes(*names):
    with UnitOfWork() as uow:
        for name in names:
            assert uow.recipes.try_add(Recipe(name=name))
        uow.commit()


def add_documents(path, *ids):
    rag = SQLiteRag.create(str(path), settings={"quantize_scan": False})

    try:
        for recipe_id in ids:
            content = f"Recipe {recipe_id}"

            sentence = Sentence(
                content=content,
                embedding=b"vector",
                start_offset=0,
                end_offset=len(content),
            )

            document = Document(
                content=content,
                uri=f"recipe:{recipe_id}",
                metadata={"entity_type": "recipe", "recipe_id": recipe_id},
                chunks=[
                    Chunk(content=content, embedding=b"vector", sentences=[sentence])
                ],
            )

            rag._repository.add_document(document)
    finally:
        rag.close()


def stored_uris(path):
    with sqlite3.connect(path) as connection:
        return {row[0] for row in connection.execute("SELECT uri FROM documents")}


def test_schema_initialization_tracks_deletions_in_existing_databases(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'old.db').as_posix()}")
    db = DatabaseEngine(engine, sessionmaker(bind=engine), database_engine.Base)
    database_engine.Base.metadata.create_all(engine)

    try:
        db.initialize_schema()
        db.initialize_schema()

        with engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO recipes (id, name, type) VALUES (?, ?, ?)",
                (42, "Existing", "unknown"),
            )

            connection.exec_driver_sql("DELETE FROM recipes WHERE id = ?", (42,))
        with engine.connect() as connection:
            assert (
                connection.exec_driver_sql(
                    "SELECT recipe_id FROM recipe_embedding_deletions"
                ).scalar_one()
                == 42
            )
    finally:
        engine.dispose()


def test_committed_delete_removes_only_deleted_recipe_and_related_index_rows(databases):
    db, config, path = databases
    add_recipes("First", "Second")
    add_documents(path, 1, 2)

    with UnitOfWork() as uow:
        uow.recipes.delete("First")
        uow.commit()
        assert not uow.embedding_cleanup_failed

    assert stored_uris(path) == {"recipe:2"}

    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM sentences").fetchone()[0] == 1

        assert (
            connection.execute(
                "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'Recipe'"
            ).fetchone()[0]
            == 1
        )


def test_rollback_and_missing_recipe_do_not_remove_embedding(databases):
    db, config, path = databases
    add_recipes("First")
    add_documents(path, 1)

    with pytest.raises(RuntimeError, match="abort"):
        with UnitOfWork() as uow:
            uow.recipes.delete("First")
            uow._session.flush()
            raise RuntimeError("abort")

    with UnitOfWork() as uow:
        with pytest.raises(ValueError):
            uow.recipes.delete("Missing")

        uow.commit()

    assert stored_uris(path) == {"recipe:1"}
    assert RecipeEmbeddingCleanup(config, db).cleanup()["removed"] == 0


def test_failed_delete_commit_leaves_recipe_and_embedding_untouched(
    databases, monkeypatch
):
    db, config, path = databases
    add_recipes("First")
    add_documents(path, 1)

    with UnitOfWork() as uow:
        uow.recipes.delete("First")

        monkeypatch.setattr(
            uow._session,
            "commit",
            lambda: (_ for _ in ()).throw(RuntimeError("commit failed")),
        )

        with pytest.raises(RuntimeError, match="commit failed"):
            uow.commit()

    with db.get_db() as session:
        assert session.get(RecipeEntity, 1) is not None

    assert stored_uris(path) == {"recipe:1"}


def test_bulk_delete_is_processed_after_commit(databases):
    db, config, path = databases
    add_recipes("First", "Second")
    add_documents(path, 1, 2)

    with UnitOfWork() as uow:
        uow._session.execute(delete(RecipeEntity).where(RecipeEntity.name == "First"))
        uow.commit()

    assert stored_uris(path) == {"recipe:2"}


def test_cleanup_removes_old_orphans_but_preserves_live_recipes(databases):
    db, config, path = databases
    add_recipes("First")
    add_documents(path, 1, 99)
    cleanup = RecipeEmbeddingCleanup(config, db)
    assert cleanup.cleanup()["removed"] == 1
    assert cleanup.cleanup()["removed"] == 0
    assert stored_uris(path) == {"recipe:1"}


def test_cleanup_preserves_unrecognized_and_non_recipe_documents(databases):
    db, config, path = databases
    add_documents(path, 1, 2, 3)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE documents SET uri = 'recipe:01' WHERE uri = 'recipe:1'"
        )
        connection.execute(
            "UPDATE documents SET uri = 'other:2' WHERE uri = 'recipe:2'"
        )

    result = RecipeEmbeddingCleanup(config, db).cleanup()
    assert result == {"removed": 1, "unrecognized": 1}
    assert stored_uris(path) == {"recipe:01", "other:2"}


def test_cleanup_does_not_create_a_missing_sidecar(databases):
    db, config, path = databases
    assert RecipeEmbeddingCleanup(config, db).cleanup()["removed"] == 0
    assert not path.exists()


def test_cleanup_failure_keeps_recipe_deleted_and_is_retryable(databases, monkeypatch):
    db, config, path = databases
    add_recipes("First")
    add_documents(path, 1)
    original = RecipeEmbeddingCleanup.cleanup_pending

    def fail(cleanup):
        raise RuntimeError("sidecar unavailable")

    monkeypatch.setattr(RecipeEmbeddingCleanup, "cleanup_pending", fail)

    with UnitOfWork() as uow:
        uow.recipes.delete("First")
        uow.commit()
        assert uow.embedding_cleanup_failed

    with db.get_db() as session:
        assert session.get(RecipeEntity, 1) is None

    assert stored_uris(path) == {"recipe:1"}

    monkeypatch.setattr(RecipeEmbeddingCleanup, "cleanup_pending", original)
    assert RecipeEmbeddingCleanup(config, db).cleanup()["removed"] == 1
    assert stored_uris(path) == set()


def test_partial_cleanup_failure_can_be_retried(databases, monkeypatch):
    from sqlite_rag.repository import Repository

    db, config, path = databases
    add_recipes("First", "Second")
    add_documents(path, 1, 2)
    original = Repository.remove_document
    calls = []

    def remove(repository, document_id):
        calls.append(document_id)
        if len(calls) == 2:
            raise RuntimeError("sidecar failure")
        return original(repository, document_id)

    monkeypatch.setattr(Repository, "remove_document", remove)

    with UnitOfWork() as uow:
        uow._session.execute(delete(RecipeEntity))
        uow.commit()
        assert uow.embedding_cleanup_failed

    assert len(stored_uris(path)) == 1
    monkeypatch.setattr(Repository, "remove_document", original)
    assert RecipeEmbeddingCleanup(config, db).cleanup()["removed"] == 1
    assert stored_uris(path) == set()


def test_pending_deletion_does_not_remove_embedding_for_reused_id(databases):
    db, config, path = databases
    add_recipes("First")
    add_documents(path, 1)

    with db.engine.begin() as connection:
        connection.execute(delete(RecipeEntity).where(RecipeEntity.id == 1))
        connection.execute(
            RecipeEntity.__table__.insert().values(
                id=1, name="Replacement", type="Unknown"
            )
        )

    assert RecipeEmbeddingCleanup(config, db).cleanup()["removed"] == 0
    assert stored_uris(path) == {"recipe:1"}


def test_indexing_a_deleted_recipe_does_not_create_an_orphan(databases, monkeypatch):
    db, config, path = databases
    add_recipes("First")
    recipe = Recipe(name="First")
    with UnitOfWork() as uow:
        uow.recipes.delete("First")
        uow.commit()

    calls = []
    monkeypatch.setattr(RecipeEmbeddingIndexer, "create_embedding", CREATE_EMBEDDING)

    monkeypatch.setattr(
        "recipes.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda *args: None,
    )

    monkeypatch.setattr(
        "sqlite_rag.SQLiteRag.add_text", lambda *args, **kwargs: calls.append(args)
    )

    with pytest.raises(ValueError, match="no longer exists"):
        RecipeEmbeddingIndexer(config, db).create_embedding(1, recipe)

    assert calls == []


def test_cleanup_waits_for_recipe_creation_before_checking_for_orphans(databases):
    db, config, path = databases
    add_documents(path, 99)
    started = Event()

    def cleanup():
        started.set()
        return RecipeEmbeddingCleanup(config, db).cleanup()

    with ThreadPoolExecutor(max_workers=1) as pool:
        with db.recipe_write_lock() as connection:
            future = pool.submit(cleanup)
            assert started.wait(5)

            with pytest.raises(TimeoutError):
                future.result(timeout=0.2)

            connection.exec_driver_sql(
                "INSERT INTO recipes (id, name, type) VALUES (?, ?, ?)",
                (99, "Restored", "unknown"),
            )

        assert future.result(timeout=10)["removed"] == 0

    assert stored_uris(path) == {"recipe:99"}


def test_indexing_waits_for_delete_and_does_not_restore_deleted_recipe(
    databases, monkeypatch
):
    db, config, path = databases
    add_recipes("First")
    monkeypatch.setattr(RecipeEmbeddingIndexer, "create_embedding", CREATE_EMBEDDING)

    monkeypatch.setattr(
        "recipes.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda *args: None,
    )

    calls = []

    monkeypatch.setattr(
        "sqlite_rag.SQLiteRag.add_text", lambda *args, **kwargs: calls.append(args)
    )

    started = Event()

    def index():
        started.set()
        try:
            RecipeEmbeddingIndexer(config, db).create_embedding(1, Recipe(name="First"))
        except ValueError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=1) as pool:
        with db.recipe_write_lock() as connection:
            future = pool.submit(index)
            assert started.wait(5)
            with pytest.raises(TimeoutError):
                future.result(timeout=0.2)
            connection.exec_driver_sql("DELETE FROM recipes WHERE id = ?", (1,))
        assert "no longer exists" in future.result(timeout=10)

    assert calls == []


def test_cleanup_menu_reports_failures(monkeypatch):
    from recipes.command_line_handler import CommandLineHandler

    messages = []

    monkeypatch.setattr(
        "recipes.command_line_handler.RecipeEmbeddingCleanup",
        lambda *args: SimpleNamespace(
            cleanup=lambda: (_ for _ in ()).throw(RuntimeError("database unavailable"))
        ),
    )

    monkeypatch.setattr(
        "recipes.command_line_handler.terminal.print_info", messages.append
    )

    CommandLineHandler()._cleanup_embeddings()

    assert messages == ["Recipe embedding cleanup failed: database unavailable"]
