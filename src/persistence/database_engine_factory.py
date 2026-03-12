from config.configuration import Configuration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from persistence.database_engine import DatabaseEngine


class DatabaseEngineFactory:
    """
    Configures the database engine with the necessary parameters.
    This class is responsible for setting up the database engine using the configuration defined in the configuration module.
    """

    def __init__(self, configuration: Configuration):
        """
        Initializes the factory with the provided configuration.

        :param configuration: An instance of the Configuration class containing database settings.
        :type configuration: Configuration
        """
        self._configuration = configuration

    def create(self):
        """
        Configures and returns an instance of the DatabaseEngine.

        :return: An instance of the DatabaseEngine class.
        :rtype: DatabaseEngine
        """
        self._engine = create_engine(
            self._configuration.sqlite_url, echo=self._configuration.sqlite_echo
        )

        self._session = sessionmaker(
            autoflush=self._configuration.sqlite_auto_flush,
            autocommit=self._configuration.sqlite_auto_commit,
            bind=self._engine,
        )

        self._base = declarative_base()
        return DatabaseEngine(self._engine, self._session, self._base)


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
database_engine_factory = DatabaseEngineFactory(Configuration())
database_engine = database_engine_factory.create()
