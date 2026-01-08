class Recipe:
    def __init__(self):
        """
        Initializes the Recipe.

        :param self: This instance of the Recipe class.
        """
        self.name = ""
        self.ingredients = []
        self.instructions = ""

    def add_ingredient(self, ingredient: tuple[int, dict]):
        """
        Adds an ingredient to the recipe.

        :param self: This instance of the Recipe class.
        :param ingredient: The ingredient to add with quantity information.
        """
        self.ingredients.append(ingredient)

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

        return md
