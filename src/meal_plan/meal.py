from recipes.recipe import Recipe
from dataclasses import dataclass


@dataclass
class Meal:
    """
    Represents a meal, which consists of a recipe and potentially other attributes such as nutrition information.

    :param recipe: The Recipe object associated with this meal.
    :type recipe: Recipe | None
    """

    recipe: Recipe | None = None

    # TODO: Calculate nutrition info based on the recipe and the persons in the household.
