import os
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import Engine


class DatabaseMaintenance:
    """
    Provides explicitly requested SQLite database maintenance.
    """

    def __init__(self, engine: Engine):
        """
        Initializes maintenance for the given SQLite engine.

        :param engine: The engine connected to the database to maintain.
        :type engine: Engine
        """
        self.__engine = engine

    def statistics(self) -> dict[str, int]:
        """
        Gets the SQLite database size and completely free page size.

        :return: The database and free-page sizes in bytes.
        :rtype: dict[str, int]
        """
        with self.__engine.connect() as connection:
            page_size = connection.exec_driver_sql("PRAGMA page_size").scalar_one()
            page_count = connection.exec_driver_sql("PRAGMA page_count").scalar_one()
            free_pages = connection.exec_driver_sql("PRAGMA freelist_count").scalar_one()

        return {
            "database_bytes": page_size * page_count,
            "free_bytes": page_size * free_pages,
        }

    def compact(self):
        """
        Rebuilds a SQLite database copy and replaces the original only if safe.

        :raises sqlalchemy.exc.SQLAlchemyError: If compaction fails.
        :raises OSError: If the compacted database cannot replace the original.
        :raises RuntimeError: If safe compaction is not possible.
        """
        database = self.__engine.url.database

        if (
            self.__engine.dialect.name != "sqlite"
            or not database
            or database == ":memory:"
        ):
            raise RuntimeError("Compaction requires a file-backed SQLite database.")
        
        database_path = Path(database).resolve()

        if not database_path.is_file():
            raise RuntimeError("The SQLite database file does not exist.")

        self.__engine.dispose()

        with TemporaryDirectory(
            prefix=".database-compact-", dir=database_path.parent
        ) as temp:
            compacted_path = Path(temp) / "compacted.db"

            try:
                with self.__engine.connect().execution_options(
                    isolation_level="AUTOCOMMIT"
                ) as connection:
                    journal_mode = connection.exec_driver_sql(
                        "PRAGMA journal_mode"
                    ).scalar_one()

                    if journal_mode.lower() != "delete":
                        raise RuntimeError(
                            "Compaction requires SQLite DELETE journal mode. "
                            "Close other applications and checkpoint the database first."
                        )

                    connection.exec_driver_sql("PRAGMA locking_mode=EXCLUSIVE")
                    connection.exec_driver_sql("BEGIN EXCLUSIVE")
                    connection.exec_driver_sql("COMMIT")
                    connection.exec_driver_sql("VACUUM INTO ?", (str(compacted_path),))

                    connection.exec_driver_sql(
                        "ATTACH DATABASE ? AS compacted", (str(compacted_path),)
                    )

                    has_sentences = connection.exec_driver_sql(
                        "SELECT EXISTS(SELECT 1 FROM main.sqlite_master "
                        "WHERE type = 'table' AND name = 'sentences')"
                    ).scalar_one()

                    if has_sentences:
                        changed = connection.exec_driver_sql(
                            """
                            SELECT EXISTS (
                                SELECT 1 FROM main.sentences AS original
                                LEFT JOIN compacted.sentences AS copied
                                    ON original.id = copied.id
                                WHERE copied.id IS NULL OR original.rowid != copied.rowid
                            )
                            """
                        ).scalar_one()

                        if changed:
                            raise RuntimeError(
                                "Compaction would change sentence row IDs and invalidate "
                                "the vector index; the original database was not changed."
                            )
                        
                    connection.exec_driver_sql("DETACH DATABASE compacted")
            finally:
                self.__engine.dispose()
                
            os.replace(compacted_path, database_path)
