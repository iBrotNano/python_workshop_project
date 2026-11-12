from config.configuration import Configuration
from persistence.retriever import Retriever


class RetrieverManager:
    """
    Reuses a retriever until the database is changed or the application exits.
    """

    def __init__(self):
        """
        Initializes an empty retriever manager.
        """
        self.__retriever: Retriever | None = None
        self.__database_path: str | None = None

    def get(
        self, configuration: Configuration, database_path: str | None = None
    ) -> Retriever:
        """
        Gets the retriever for the configured database.

        :param configuration: Application configuration.
        :type configuration: Configuration
        :param database_path: Optional path to the database to retrieve from.
        :type database_path: str | None
        :return: An open retriever.
        :rtype: Retriever
        """
        requested_path = database_path or configuration.sqlite_file_path

        if self.__database_path != requested_path:
            self.close()

        if self.__retriever is None:
            self.__retriever = (
                Retriever(configuration)
                if database_path is None
                else Retriever(configuration, requested_path)
            )
            self.__database_path = requested_path
            
        return self.__retriever

    def close(self):
        """
        Closes and forgets the current retriever.
        """
        if self.__retriever is not None:
            self.__retriever.close()
            self.__retriever = None
            self.__database_path = None


retriever_manager = RetrieverManager()
