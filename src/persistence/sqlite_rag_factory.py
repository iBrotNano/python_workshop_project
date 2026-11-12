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

    def create_for_retrieval(self) -> SQLiteRag:
        """
        Opens the configured database for retrieval without creating it.

        :return: An SQLiteRag instance for the existing database.
        :rtype: SQLiteRag
        """
        return SQLiteRag.create(
            self.__configuration.sqlite_file_path,
            require_existing=True,
        )

    def create_for_embedding(self, quantize_scan: bool = False) -> SQLiteRag:
        """
        Creates an SQLiteRag instance configured for embedding operations.

        :param quantize_scan: Whether to use quantized vector scanning.
        :type quantize_scan: bool
        :return: A configured SQLiteRag instance.
        :rtype: SQLiteRag
        """
        Settings.use_gpu = self.__configuration.ai_use_vulcan_llama_backend

        return SQLiteRag.create(
            self.__configuration.sqlite_file_path,
            settings={
                "model_path": self.__configuration.ai_used_embedding_model_path,
                "chunk_size": self.__configuration.ai_embedding_chunk_size,
                "chunk_overlap": self.__configuration.ai_embedding_chunk_overlap,
                "quantize_scan": quantize_scan,
            },
        )
