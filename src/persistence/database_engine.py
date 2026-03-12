from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Any, Generator
from persistence.model_registry import load_model_definitions


class DatabaseEngine:
    """
    Encapsulates the SQLAlchemy engine, session, and base for database operations.
    """

    def __init__(self, engine: Engine, session: sessionmaker, base: Any):
        """
        Initializes the DatabaseEngine with the provided SQLAlchemy engine, session, and base.

        :param engine: The SQLAlchemy engine instance.
        :type engine: Engine
        :param session: The SQLAlchemy sessionmaker instance.
        :type session: sessionmaker
        :param base: The SQLAlchemy declarative base.
        :type base: Any
        """
        self._engine: Engine = engine
        self.session: sessionmaker = session
        self.Base: Any = base

    def initialize_schema(self):
        """
        Creates all registered SQLAlchemy tables.

        :param self: The instance of the DatabaseEngine class.
        """
        load_model_definitions()
        self.Base.metadata.create_all(bind=self._engine)

    def get_db(self) -> Generator[Session, None, None]:
        """
        Provides a database session for performing operations. This method is a generator that yields a session and ensures it is properly closed after use.

        :return: A generator yielding a SQLAlchemy session.
        :rtype: Generator[Session, None, None]
        """
        db = self.session()

        try:
            yield db
        finally:
            db.close()
