from sqlalchemy import Column, Integer, Float, String, Enum
from persistence.database_engine_factory import database_engine
from persons.gender import Gender


class PersonEntity(database_engine.Base):
    """
    SQLAlchemy entity representing a person in the database. This class defines the structure of the 'persons' table and its columns.
    """

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    gender = Column(
        Enum(*[g.value for g in Gender]), nullable=False, default=Gender.MALE.value
    )

    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    birth_year = Column(Integer, nullable=False)
    # TODO: Change activity level into table and remove the hardcoded mapping.
    activity_level = Column(Integer, nullable=False)
