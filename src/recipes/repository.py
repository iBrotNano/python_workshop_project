from recipes.recipe import Recipe
import yaml
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

        self._write_yaml(
            {name: self._to_dict(recipe) for name, recipe in self.recipes.items()}
        )

    def delete(self, recipe_name: str):
        """
        Deletes a recipe from the repository.

        :param self: This instance of the Repository class.
        :param recipe_name: The name of the recipe to delete.
        :type recipe_name: str
        """
        if recipe_name in self.recipes:
            del self.recipes[recipe_name]
            self.save()

    def _load(self):
        """
        Loads the recipes from disk.
        """
        data = self._read_yaml()

        self.recipes = {
            name: self._from_dict(payload) for name, payload in data.items()
        }

    def _ensure_storage_path_exists(self):
        """
        Ensures the storage directory exists.
        """
        path = Path(config.recipes_storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def _write_yaml(self, obj):
        """
        Writes the given object as YAML to disk.

        :param self: This instance of the Repository class.
        :param obj: The object to write as YAML.
        :type obj: Any
        """
        self._ensure_storage_path_exists()

        with open(
            config.recipes_storage_path.absolute(), "w", encoding="utf-8"
        ) as file:
            yaml.dump(obj, file, default_flow_style=False, allow_unicode=True)

    def _read_yaml(self):
        """
        Reads the YAML data from disk.

        :param self: This instance of the Repository class.
        :return: The YAML data read from disk.
        """
        self._ensure_storage_path_exists()

        if not config.recipes_storage_path.exists():
            return {}

        with open(
            config.recipes_storage_path.absolute(), "r", encoding="utf-8"
        ) as file:
            return yaml.safe_load(file) or {}

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
            "ingredients": [  # yaml does not support tuples
                {"amount": amount, "product": product}
                for amount, product in recipe.ingredients
            ],
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
        ingredients = data.get("ingredients", [])
        # Convert dictionary format to tuples (amount, product)
        instance.ingredients = [
            (item["amount"], item["product"]) for item in ingredients
        ]
        instance.instructions = data.get("instructions", "")
        return instance
