from sqlalchemy import Column, ForeignKey, Integer
from persistence.database_engine_factory import database_engine
from sqlalchemy.orm import relationship


class MealEntity(database_engine.Base):
    """
    SQLAlchemy entity representing a meal in the database. This class defines the structure of the 'meals' table and its columns.
    """

    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)

    meal_plan_id = Column(
        Integer, ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False
    )

    meal_plan = relationship("MealPlanEntity", back_populates="meals")

    recipe_id = Column(
        Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True
    )

    recipe = relationship("RecipeEntity", back_populates="meals")

    persons = relationship(
        "PersonEntity",
        secondary="meal_person_association",
        back_populates="meals",
    )
