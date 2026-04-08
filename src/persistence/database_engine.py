from contextlib import contextmanager
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
        self._seed_activity_levels()

    def _seed_activity_levels(self):
        """
        Inserts default activity levels if they do not exist and synchronizes changed values.

        :param self: The instance of the DatabaseEngine class.
        """
        # The import is placed here to avoid circular imports, as the Repository class also imports the DatabaseEngine.
        from persons.activity_level_entity import ActivityLevelEntity

        # TODO: The default data is hardcoded. Maybe storing them as a JSON file or similar would be better?
        default_activity_levels = {
            1: ("Sedentary (little or no exercise)", 1.2),
            2: ("Lightly active (light exercise/sports 1-3 days/week)", 1.375),
            3: ("Moderately active (moderate exercise/sports 3-5 days/week)", 1.55),
            4: ("Very active (hard exercise/sports 6-7 days a week)", 1.725),
            5: ("Super active (very hard exercise & physical job or 2x training)", 1.9),
        }

        db: Session = self.session()

        try:
            for id, (name, multiplier) in default_activity_levels.items():
                entity = db.get(ActivityLevelEntity, id)

                if entity is None:
                    db.add(
                        ActivityLevelEntity(
                            id=id,
                            name=name,
                            multiplier=multiplier,
                        )
                    )

                    continue

                entity.name = name
                entity.multiplier = multiplier

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """
        Provides a database session for performing operations.
        This method is a generator that yields a session and ensures
        it is properly closed after use.

        By decorating this method with @contextmanager, it can be used in a
        with statement to automatically manage the session's lifecycle.

        :return: A generator yielding a SQLAlchemy session.
        :rtype: Generator[Session, None, None]
        """
        db = self.session()

        try:
            yield db
        finally:
            db.close()
