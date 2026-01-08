from recipes.recipe import Recipe
import json
import config.config as config
from pathlib import Path


class Repository:
    def __init__(self):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        self.recipes = {}
        self._load()

    def try_add(self, recipe: Recipe):
        """
        Tries to add a recipe to the repository if it does not already exist.

        :param self: This instance of the Repository class.
        :param recipe: The recipe to add.
        :type recipe: Recipe
        """
        if recipe.name in self.recipes:
            return False  # Recipe already exists.

        self.recipes[recipe.name] = recipe
        return True

    def save(self):
        """
        Stores the recipes to disk.
        """

        self._write_json(
            {name: self._to_dict(recipe) for name, recipe in self.recipes.items()}
        )

    def _load(self):
        """
        Loads the recipes from disk.
        """
        data = self._read_json()

        self.recipes = {
            name: self._from_dict(payload) for name, payload in data.items()
        }

    def _ensure_storage_path_exists(self):
        """
        Ensures the storage directory exists.
        """
        path = Path(config.recipes_storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def _write_json(self, obj):
        """
        Writes the given object as JSON to disk.

        :param self: This instance of the Repository class.
        :param obj: The object to write as JSON.
        :type obj: Any
        """
        self._ensure_storage_path_exists()

        with open(
            config.recipes_storage_path.absolute(), "w", encoding="utf-8"
        ) as file:
            json.dump(obj, file, indent=4, ensure_ascii=False)

    def _read_json(self):
        """
        Reads the JSON data from disk.

        :param self: This instance of the Repository class.
        :return: The JSON data read from disk.
        """
        self._ensure_storage_path_exists()

        if not config.recipes_storage_path.exists():
            return {}

        with open(
            config.recipes_storage_path.absolute(), "r", encoding="utf-8"
        ) as file:
            return json.load(file)

    def _to_dict(self, recipe: Recipe) -> dict:
        """
        Converts a Recipe instance to a dictionary.

        :param recipe: The recipe to convert.
        :type recipe: Recipe
        :return: The recipe as a dictionary.
        :rtype: dict
        """
        return {
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
        }

    def _from_dict(self, data: dict) -> Recipe:
        """
        Converts a dictionary to a Recipe instance.

        :param data: The dictionary containing recipe data.
        :type data: dict
        :return: The instantiated Recipe object.
        :rtype: Recipe
        """
        instance = Recipe()
        instance.name = data.get("name")
        instance.ingredients = data.get("ingredients", [])
        instance.instructions = data.get("instructions", "")
        return instance
