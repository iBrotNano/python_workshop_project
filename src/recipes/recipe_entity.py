from sqlalchemy import Column, Integer, String, Enum, JSON, Text
from persistence.database_engine_factory import database_engine
from recipes.recipe_type import RecipeType


class RecipeEntity(database_engine.Base):
    """
    Represents a recipe in the database.
    """

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    ingredients = Column(JSON)
    instructions = Column(Text)
    nutrition = Column(JSON)

    type = Column(
        Enum(*[r.value for r in RecipeType]),
        nullable=False,
        default=RecipeType.UNKNOWN.value,
    )
