from enum import Enum


class RecipeType(str, Enum):
    """
    An enumeration representing different types of recipes.
    """

    UNKNOWN = "unknown"
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
