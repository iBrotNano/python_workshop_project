from sqlalchemy import Column, ForeignKey, Integer, Table

from persistence.database_engine_factory import database_engine

meal_person_association = Table(
    "meal_person_association",
    database_engine.Base.metadata,
    Column("meal_id", Integer, ForeignKey("meals.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)
