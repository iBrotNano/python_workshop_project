from pathlib import Path
from sqlite_rag import SQLiteRag
from sqlite_rag.settings import Settings
from config.configuration import Configuration


class SQLiteRagFactory:
    """Creates SQLiteRag instances for application database workflows."""

    def __init__(self, configuration: Configuration):
        """
        Initializes the factory with application configuration.

        :param configuration: The configuration used to create SQLiteRag instances.
        :type configuration: Configuration
        """
        self.__configuration = configuration

    @property
    def recipe_database_path(self) -> str:
        """
        Gets the sidecar database path used exclusively for recipe embeddings.

        :return: The recipe embedding database path.
        :rtype: str
        """
        database_path = Path(self.__configuration.sqlite_file_path)

        return str(
            database_path.with_name(
                f"{database_path.stem}_recipes{database_path.suffix}"
            )
        )

    def create_for_retrieval(self, database_path: str | None = None) -> SQLiteRag:
        """
        Opens the configured database for retrieval without creating it.

        :param database_path: Optional path to the existing retrieval database.
        :type database_path: str | None
        :return: An SQLiteRag instance for the existing database.
        :rtype: SQLiteRag
        """
        return SQLiteRag.create(
            database_path or self.__configuration.sqlite_file_path,
            require_existing=True,
        )

    def create_for_embedding(
        self, quantize_scan: bool = False, database_path: str | None = None
    ) -> SQLiteRag:
        """
        Creates an SQLiteRag instance configured for embedding operations.

        :param quantize_scan: Whether to use quantized vector scanning.
        :type quantize_scan: bool
        :param database_path: Optional path to the database receiving embeddings.
        :type database_path: str | None
        :return: A configured SQLiteRag instance.
        :rtype: SQLiteRag
        """
        Settings.use_gpu = self.__configuration.ai_use_vulcan_llama_backend

        return SQLiteRag.create(
            database_path or self.__configuration.sqlite_file_path,
            settings={
                "model_path": self.__configuration.ai_used_embedding_model_path,
                "chunk_size": self.__configuration.ai_embedding_chunk_size,
                "chunk_overlap": self.__configuration.ai_embedding_chunk_overlap,
                "quantize_scan": quantize_scan,
            },
        )

    def create_for_recipe_embedding(self) -> SQLiteRag:
        """
        Creates a SQLiteRag instance configured for recipe embeddings.

        :return: A configured SQLiteRag instance for the recipe database.
        :rtype: SQLiteRag
        """
        return self.create_for_embedding(database_path=self.recipe_database_path)
