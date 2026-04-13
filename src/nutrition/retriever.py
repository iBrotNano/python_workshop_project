from sqlite_rag import SQLiteRag
from config.configuration import Configuration


class Retriever:
    def __init__(self, configuration: Configuration):
        """
        Initializes the Retriever instance with the provided configuration.

        :param configuration: The configuration object containing settings for the retriever.
        :type configuration: Configuration
        """
        self.rag = SQLiteRag.create(
            configuration.sqlite_file_path,
            require_existing=True,
        )

    def close(self):
        """
        Closes the Retriever instance and releases any resources.
        """
        if self.rag is not None:
            self.rag.close()

    def __enter__(self) -> "Retriever":
        """
        Enters the runtime context related to this object.

        :return: The Retriever instance.
        :rtype: Retriever

        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the runtime context related to this object.

        :param exc_type: The exception type, if any.
        :param exc_value: The exception value, if any.
        :param traceback: The traceback object, if any.
        """
        self.close()

    def retrieve(self, query: str, top_k: int = 10):
        """
        Retrieves relevant nutrition information based on the provided query.

        :param query: The search query to retrieve nutrition information for.
        :type query: str
        :param top_k: The number of top results to return, default is 10.
        :type top_k: int
        :return: A list of retrieved results matching the query.
        :rtype: list
        """
        return self.rag.search(query, top_k=top_k)
