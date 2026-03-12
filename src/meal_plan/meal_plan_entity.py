from sqlalchemy import Column, Integer
from persistence.database_engine_factory import database_engine
from sqlalchemy.orm import relationship


class MealPlanEntity(database_engine.Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)

    meals = relationship(
        "MealEntity", back_populates="meal_plan", cascade="all, delete-orphan"
    )
