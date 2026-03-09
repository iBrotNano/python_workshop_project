import logging
from pathlib import Path

log = logging.getLogger(__name__)


class Recipe:
    def __init__(
        self,
        name: str = "",
        ingredients: list = [],
        instructions: str = "",
        nutrition: dict = {},
        type: str = "unknown",
    ):
        """
        Initializes the Recipe.

        :param self: This instance of the Recipe class.
        """
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.nutrition = nutrition
        self.type = type  # e.g., breakfast, lunch, dinner, snack

    def add_ingredient(self, ingredient: dict):
        """
        Adds an ingredient to the recipe.

        :param self: This instance of the Recipe class.
        :param ingredient: The ingredient to add with quantity information.
        """
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
            md += f"- {ingredient['amount']}g [{ingredient['food']['brands']} {ingredient['food']['product']}]({ingredient['food']['url']})\n"

        md += "\n## Instructions\n\n"
        md += self.instructions + "\n"
        md += "\n## Nutritional Information\n\n"
        md += "| Nutrient        | Amount          |\n"
        md += "|:----------------|----------------:|\n"

        for nutrient, amount in self.get_formatted_nutrition().items():
            md += f"| {nutrient.ljust(15)} | {amount.ljust(15)} |\n"

        return md

    def get_formatted_nutrition(self) -> dict:
        """
        Returns the nutritional information with formatted values.

        :param self: This instance of the Recipe class.
        :return: The formatted nutritional information.
        :rtype: dict
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

    def export_as_markdown(self, file_path: str):
        """
        Exports the recipe as a markdown file.

        :param self: This instance of the Recipe class.
        :param file_path: The file path to save the markdown file.
        :type file_path: str
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.as_markdown())

    def _calculate_nutrition(self) -> dict:
        """
        Calculates the total nutritional information for the recipe.

        :param self: This instance of the Recipe class.
        :return: The total nutritional information for the recipe.
        :rtype: dict
        """
        nutrition = {
            "calories": 0,
            "energy": 0,
            "fat": 0,
            "carbohydrates": 0,
            "protein": 0,
            "sugar": 0,
            "salt": 0,
        }

        # Map ingredient nutrient keys to recipe nutrition keys
        nutrient_mappings = [
            ("energy-kcal_100g", "calories"),
            ("energy-kj_100g", "energy"),
            ("fat_100g", "fat"),
            ("carbohydrates_100g", "carbohydrates"),
            ("proteins_100g", "protein"),
            ("sugars_100g", "sugar"),
            ("salt_100g", "salt"),
        ]

        for ingredient in self.ingredients:
            factor = ingredient["amount"] / 100.0  # Nutritional information is per 100g

            for ingredient_key, nutrition_key in nutrient_mappings:
                # Skip calculation if this nutrient is already marked as unavailable
                if nutrition[nutrition_key] == "N/A":
                    continue

                try:
                    value = float(ingredient["food"].get(ingredient_key, "N/A"))
                    nutrition[nutrition_key] += value * factor
                except (ValueError, TypeError):
                    # Mark this nutrient as unavailable if conversion fails
                    nutrition[nutrition_key] = "N/A"
                    log.warning(
                        f"Missing or invalid value for '{ingredient_key}' "
                        f"in {ingredient['food'].get('product', 'unknown')}. "
                        f"Nutrient '{nutrition_key}' cannot be calculated."
                    )

        return nutrition
