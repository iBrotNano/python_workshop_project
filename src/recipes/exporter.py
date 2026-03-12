from pathlib import Path
from recipes.recipe import Recipe


class Exporter:
    """A class responsible for exporting recipes in different formats."""

    def __init__(self, recipe: Recipe):
        """
        Initializes the Exporter with a Recipe instance.

        :param self: This instance of the Exporter class.
        :param recipe: The recipe to be exported.
        :type recipe: Recipe
        """
        self._recipe = recipe

    def export_as_markdown(self, file_path: str):
        """
        Exports the recipe as a markdown file.

        :param self: This instance of the Exporter class.
        :param file_path: The file path to save the markdown file.
        :type file_path: str
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self._recipe.as_markdown())
