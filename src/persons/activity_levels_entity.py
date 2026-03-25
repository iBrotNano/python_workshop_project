from persistence.database_engine_factory import database_engine
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship


class ActivityLevelsEntity(database_engine.Base):
    """
    SQLAlchemy entity representing an activity level in the database. This class defines the structure of the 'activity_levels' table and its columns.
    """

    __tablename__ = "activity_levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    multiplier = Column(Float, nullable=False)

    persons = relationship(
        "PersonEntity",
        back_populates="activity_level",
    )
