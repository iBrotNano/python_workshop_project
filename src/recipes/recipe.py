class Recipe:
    def __init__(self):
        """
        Initializes the Recipe.

        :param self: This instance of the Recipe class.
        """
        self.name = ""
        self.ingredients = []
        self.instructions = ""
        self.nutrition = {}

    def add_ingredient(self, ingredient: tuple[int, dict]):
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
        md = f"# {self.name}\n\n"

        md += "## Ingredients\n\n"

        for amount, ingredient in self.ingredients:
            md += f"- {amount}g [{ingredient['brands']} {ingredient['product']}]({ingredient['url']})\n"

        md += "\n## Instructions\n\n"
        md += self.instructions + "\n"
        md += "\n## Nutritional Information\n\n"
        md += "| Nutrient       | Amount          |\n"
        md += "|:---------------|----------------:|\n"

        for nutrient, value in self.nutrition.items():
            md += f"| {nutrient.capitalize()} | {value:.2f} {'kcal' if nutrient == 'calories' else 'kJ' if nutrient == 'energy' else 'g'} |\n"

        return md

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

        for amount, ingredient in self.ingredients:
            factor = amount / 100.0  # Nutritional information is per 100g

            nutrition["calories"] += (
                float(ingredient.get("energy-kcal_100g", 0)) * factor
            )

            nutrition["energy"] += float(ingredient.get("energy-kj_100g", 0)) * factor
            nutrition["fat"] += float(ingredient.get("fat_100g", 0)) * factor

            nutrition["carbohydrates"] += (
                float(ingredient.get("carbohydrates_100g", 0)) * factor
            )

            nutrition["protein"] += float(ingredient.get("proteins_100g", 0)) * factor
            nutrition["sugar"] += float(ingredient.get("sugars_100g", 0)) * factor
            nutrition["salt"] += float(ingredient.get("salt_100g", 0)) * factor

        return nutrition
