import sqlite3
from contextlib import closing

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError

from persistence.database_maintenance import DatabaseMaintenance


def test_compaction_reclaims_free_pages_and_preserves_all_tables(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'data.db').as_posix()}")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE nutrition (id INTEGER PRIMARY KEY, value TEXT)")
        connection.exec_driver_sql("CREATE TABLE documents (id INTEGER PRIMARY KEY, value TEXT)")
        connection.exec_driver_sql("CREATE TABLE persons (id INTEGER PRIMARY KEY, value TEXT)")
        connection.exec_driver_sql("INSERT INTO documents VALUES (1, 'embedding document')")
        connection.exec_driver_sql("INSERT INTO persons VALUES (1, 'person')")
        connection.exec_driver_sql("INSERT INTO nutrition VALUES (1, 'retained')")
        connection.exec_driver_sql(
            "INSERT INTO nutrition VALUES (2, ?)", ("x" * 1000000,)
        )
        connection.exec_driver_sql("DELETE FROM nutrition WHERE id = 2")

    maintenance = DatabaseMaintenance(engine)
    before = maintenance.statistics()
    assert before["free_bytes"] > 0

    maintenance.compact()

    after = maintenance.statistics()
    assert after["free_bytes"] == 0
    assert after["database_bytes"] < before["database_bytes"]
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT value FROM nutrition").scalar_one() == "retained"
        assert connection.exec_driver_sql("SELECT value FROM documents").scalar_one() == "embedding document"
        assert connection.exec_driver_sql("SELECT value FROM persons").scalar_one() == "person"
    engine.dispose()


def test_compaction_propagates_database_lock_error(tmp_path):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'data.db').as_posix()}",
        connect_args={"timeout": 0.1},
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE nutrition (id INTEGER)")
    connection = engine.connect()
    transaction = connection.begin()
    connection.exec_driver_sql("INSERT INTO nutrition VALUES (1)")
    try:
        with pytest.raises(OperationalError, match="locked"):
            DatabaseMaintenance(engine).compact()
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


def test_compaction_cancellation_does_not_close_retriever_or_vacuum(monkeypatch):
    from types import SimpleNamespace

    from persistence.command_line_handler import CommandLineHandler

    actions = []
    monkeypatch.setattr(
        "persistence.command_line_handler.DatabaseMaintenance",
        lambda engine: SimpleNamespace(
            statistics=lambda: {"database_bytes": 100, "free_bytes": 20},
            compact=lambda: actions.append("compact"),
        ),
    )
    monkeypatch.setattr(
        "persistence.command_line_handler.retriever_manager",
        SimpleNamespace(close=lambda: actions.append("close")),
    )
    monkeypatch.setattr(
        "persistence.command_line_handler.terminal",
        SimpleNamespace(
            print_info=lambda message: None,
            safe_confirm=lambda *args, **kwargs: False,
        ),
    )

    CommandLineHandler().compact()

    assert actions == []


def test_confirmed_compaction_closes_retriever_and_reports_result(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace

    from persistence.command_line_handler import CommandLineHandler

    actions = []
    messages = []
    monkeypatch.setattr(
        "persistence.command_line_handler.DatabaseMaintenance",
        lambda engine: SimpleNamespace(
            statistics=lambda: {"database_bytes": 100, "free_bytes": 20},
            compact=lambda: actions.append("compact"),
        ),
    )
    monkeypatch.setattr(
        "persistence.command_line_handler.retriever_manager",
        SimpleNamespace(close=lambda: actions.append("close")),
    )
    monkeypatch.setattr(
        "persistence.command_line_handler.terminal",
        SimpleNamespace(
            print_info=messages.append,
            safe_confirm=lambda *args, **kwargs: True,
            console=SimpleNamespace(status=lambda message: nullcontext()),
        ),
    )

    CommandLineHandler().compact()

    assert actions == ["close", "compact"]
    assert "completed" in messages[-1]


def test_failed_database_replacement_preserves_original(tmp_path, monkeypatch):
    database_path = tmp_path / "data.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE nutrition (id INTEGER)")
        connection.exec_driver_sql("INSERT INTO nutrition VALUES (1)")

    def fail_replace(source, destination):
        raise OSError("replacement failed")

    monkeypatch.setattr("persistence.database_maintenance.os.replace", fail_replace)
    with pytest.raises(OSError, match="replacement failed"):
        DatabaseMaintenance(engine).compact()

    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT id FROM nutrition").scalar_one() == 1
    assert sorted(path.name for path in tmp_path.iterdir()) == ["data.db"]
    engine.dispose()


def test_compaction_rejects_sentence_rowid_changes_without_touching_original(tmp_path):
    database_path = tmp_path / "data.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE sentences (id TEXT, chunk_id INTEGER)"
        )
        connection.exec_driver_sql(
            "INSERT INTO sentences (id, chunk_id) VALUES ('a', 1), ('b', 1), ('c', 1)"
        )
        connection.exec_driver_sql("DELETE FROM sentences WHERE id = 'b'")
        original = connection.exec_driver_sql(
            "SELECT id, rowid FROM sentences ORDER BY id"
        ).fetchall()

    def alter_compacted_rowid(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("VACUUM INTO"):
            with closing(sqlite3.connect(parameters[0])) as compacted:
                compacted.execute("UPDATE sentences SET rowid = 20 WHERE id = 'c'")
                compacted.commit()

    event.listen(engine, "after_cursor_execute", alter_compacted_rowid)
    with pytest.raises(RuntimeError, match="sentence row IDs"):
        DatabaseMaintenance(engine).compact()

    with engine.connect() as connection:
        assert connection.exec_driver_sql(
            "SELECT id, rowid FROM sentences ORDER BY id"
        ).fetchall() == original
    assert sorted(path.name for path in tmp_path.iterdir()) == ["data.db"]
    engine.dispose()


def test_compaction_rejects_wal_mode_without_replacing_database(tmp_path):
    database_path = tmp_path / "data.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA journal_mode=WAL")
        connection.exec_driver_sql("CREATE TABLE nutrition (id INTEGER)")
        connection.exec_driver_sql("INSERT INTO nutrition VALUES (1)")
        connection.commit()

    with pytest.raises(RuntimeError, match="DELETE journal mode"):
        DatabaseMaintenance(engine).compact()

    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT id FROM nutrition").scalar_one() == 1
    engine.dispose()


def test_compaction_preserves_existing_sentence_rowids(tmp_path):
    database_path = tmp_path / "data.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE sentences (id TEXT PRIMARY KEY, chunk_id INTEGER)"
        )
        connection.exec_driver_sql(
            "INSERT INTO sentences (id, chunk_id) VALUES ('a', 1), ('b', 1)"
        )
        before = connection.exec_driver_sql(
            "SELECT id, rowid FROM sentences ORDER BY id"
        ).fetchall()

    DatabaseMaintenance(engine).compact()

    with engine.connect() as connection:
        assert connection.exec_driver_sql(
            "SELECT id, rowid FROM sentences ORDER BY id"
        ).fetchall() == before
    engine.dispose()
