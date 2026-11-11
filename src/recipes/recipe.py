import logging

from dataclasses import dataclass, field
from typing import Any
from nutrition.nutrition import Nutrition
from recipes.recipe_type import RecipeType

log = logging.getLogger(__name__)


@dataclass
class Recipe:
    """
    A class representing a recipe with its details, including ingredients, instructions, and nutritional information.

    :param name: The name of the recipe.
    :type name: str
    :param ingredients: The ingredients of the recipe.
    :type ingredients: list[dict[str, Any]]
    :param instructions: The instructions for the recipe.
    :type instructions: str
    :param nutrition: The nutritional information of the recipe.
    :type nutrition: dict[str, float | str]
    :param type: The type of the recipe (e.g., breakfast, lunch, dinner).
    :type type: RecipeType
    """

    name: str = ""
    ingredients: list[dict[str, Any]] = field(default_factory=list)
    instructions: str = ""
    nutrition: dict[str, float | str] = field(default_factory=dict)
    type: RecipeType = RecipeType.UNKNOWN

    def __post_init__(self):
        """Normalizes persisted values to runtime types."""
        if isinstance(self.type, str):
            try:
                self.type = RecipeType(self.type)
            except ValueError:
                self.type = RecipeType.UNKNOWN

    def add_ingredient(self, ingredient: dict[str, Any]):
        """
        Adds an ingredient to the recipe.

        :param self: This instance of the Recipe class.
        :param ingredient: An ingredient with its amount in grams and a Nutrition food.
        :type ingredient: dict[str, Any]
        :raises TypeError: If the food is not a Nutrition object.
        """
        if not isinstance(ingredient["food"], Nutrition):
            raise TypeError("Recipe ingredient food must be a Nutrition object.")

        self.ingredients.append(ingredient)
        self.nutrition = self._calculate_nutrition()

    def as_markdown(self) -> str:
        """
        Returns the recipe as a markdown string.

        :param self: This instance of the Recipe class.
        :return: The recipe as a markdown string.
        :rtype: str
        """
        md = f"# {self.name} ({self.type.capitalize()})\n\n"

        md += "## Ingredients\n\n"

        for ingredient in self.ingredients:
            food: Nutrition = ingredient["food"]
            brands = ", ".join(food.brands or [])
            md += f"- {ingredient['amount']}g [{brands} {food.name or 'unknown'}]({food.url or ''})\n"

        md += "\n## Instructions\n\n"
        md += self.instructions + "\n"
        md += "\n## Nutritional Information\n\n"
        md += "| Nutrient        | Amount          |\n"
        md += "|:----------------|----------------:|\n"

        for nutrient, amount in self.get_formatted_nutrition().items():
            md += f"| {nutrient.ljust(15)} | {amount.ljust(15)} |\n"

        return md

    def get_formatted_nutrition(self) -> dict[str, str]:
        """
        Returns the nutritional information with formatted values.

        :param self: This instance of the Recipe class.
        :return: The formatted nutritional information.
        :rtype: dict[str, str]
        """
        formatted_nutrition = {}

        for nutrient, amount in self.nutrition.items():
            if isinstance(amount, (int, float)):
                formatted_nutrition[nutrient.capitalize()] = (
                    f"{amount:.2f} {'kcal' if nutrient == 'calories' else 'kJ' if nutrient == 'energy' else 'g'}"
                )
            else:
                formatted_nutrition[nutrient.capitalize()] = str(amount)

        return formatted_nutrition

    def _calculate_nutrition(self) -> dict[str, float | str]:
        """
        Calculates the total nutritional information for the recipe.

        :param self: This instance of the Recipe class.
        :return: The total nutritional information for the recipe.
        :rtype: dict[str, float | str]
        """
        nutrition: dict[str, float | str] = {
            "calories": 0.0,
            "energy": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
            "protein": 0.0,
            "sugar": 0.0,
            "salt": 0.0,
        }

        nutrient_mappings = [
            ("energy_100g_kj", "energy"),
            ("fat_100g", "fat"),
            ("carbohydrates_100g", "carbohydrates"),
            ("proteins_100g", "protein"),
            ("sugars_100g", "sugar"),
            ("salt_100g", "salt"),
        ]

        for ingredient in self.ingredients:
            food: Nutrition = ingredient["food"]
            factor = ingredient["amount"] / 100.0

            values = [
                (
                    "energy-kcal_100g",
                    "calories",
                    ingredient.get("_legacy_food", {}).get("energy-kcal_100g"),
                )
            ]

            values.extend(
                (attribute, key, getattr(food, attribute))
                for attribute, key in nutrient_mappings
            )

            for ingredient_key, nutrition_key, nutrient_value in values:
                if nutrition[nutrition_key] == "N/A":
                    continue

                try:
                    value = float(nutrient_value)
                    nutrition[nutrition_key] += value * factor
                except (ValueError, TypeError):
                    nutrition[nutrition_key] = "N/A"

                    log.warning(
                        f"Missing or invalid value for '{ingredient_key}' "
                        f"in {food.name or 'unknown'}. "
                        f"Nutrient '{nutrition_key}' cannot be calculated."
                    )

        return nutrition
