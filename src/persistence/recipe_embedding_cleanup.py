import logging
import re

from pathlib import Path
from config.configuration import Configuration
from persistence.database_engine import DatabaseEngine
from persistence.retriever_manager import retriever_manager
from persistence.sqlite_rag_factory import SQLiteRagFactory

log = logging.getLogger(__name__)


class RecipeEmbeddingCleanup:
    """
    Reconciles recipe documents against the authoritative recipe database.
    """

    def __init__(self, configuration: Configuration, database_engine: DatabaseEngine):
        """
        Initializes cleanup for the configured recipe and vector databases.

        :param configuration: Application configuration.
        :type configuration: Configuration
        :param database_engine: Database containing the recipe rows.
        :type database_engine: DatabaseEngine
        """
        self.__database_engine = database_engine
        self.__factory = SQLiteRagFactory(configuration)

    def has_pending(self) -> bool:
        """
        Checks whether a committed recipe deletion needs reconciliation.

        :return: Whether deletion tracking contains pending work.
        :rtype: bool
        """
        with self.__database_engine.engine.connect() as connection:
            return bool(
                connection.exec_driver_sql(
                    "SELECT EXISTS(SELECT 1 FROM recipe_embedding_deletions)"
                ).scalar_one()
            )

    def cleanup_pending(self) -> dict[str, int]:
        """
        Removes embeddings for committed recipe deletions.

        :return: The number of removed and unrecognized documents.
        :rtype: dict[str, int]
        """
        return self.__reconcile(False)

    def cleanup(self) -> dict[str, int]:
        """
        Removes all orphaned recipe embeddings and reconciles pending deletions.

        :return: The number of removed and unrecognized documents.
        :rtype: dict[str, int]
        """
        return self.__reconcile(True)

    def __reconcile(self, all_orphans: bool) -> dict[str, int]:
        """
        Removes eligible documents while preventing concurrent recipe writes.

        :param all_orphans: Whether to scan all recipe documents.
        :type all_orphans: bool
        :return: Counts of removed and unrecognized documents.
        :rtype: dict[str, int]
        """
        removed = 0
        unrecognized = 0

        with self.__database_engine.recipe_write_lock() as connection:
            pending = {
                str(row[0])
                for row in connection.exec_driver_sql(
                    "SELECT recipe_id FROM recipe_embedding_deletions"
                )
            }

            if not all_orphans and not pending:
                return {"removed": 0, "unrecognized": 0}

            path = self.__factory.recipe_database_path

            if Path(path).exists():
                retriever_manager.close()
                rag = self.__factory.create_for_retrieval(path)

                try:
                    live = {
                        str(row[0])
                        for row in connection.exec_driver_sql("SELECT id FROM recipes")
                    }

                    documents = rag._conn.execute(
                        "SELECT id, uri FROM documents WHERE uri LIKE 'recipe:%'"
                    ).fetchall()

                    for document in documents:
                        uri = document["uri"]

                        if not re.fullmatch(r"recipe:[1-9][0-9]*", uri):
                            unrecognized += 1
                            log.warning("Cannot reconcile recipe document URI %r.", uri)
                            continue

                        recipe_id = uri[7:]

                        if recipe_id in live or (
                            not all_orphans and recipe_id not in pending
                        ):
                            continue

                        if not rag._repository.remove_document(document["id"]):
                            raise RuntimeError(
                                f"Could not remove recipe document {uri}."
                            )

                        removed += 1
                finally:
                    rag.close()

            connection.exec_driver_sql("DELETE FROM recipe_embedding_deletions")

        return {"removed": removed, "unrecognized": unrecognized}
