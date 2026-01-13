from common.yaml_file_repository import YamlFileRepository
from recipes.recipe import Recipe
import config.config as config
import random


class Repository(YamlFileRepository):
    def __init__(self):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        super().__init__(config.recipes_storage_path)
        self._load()

    def try_add(self, recipe: Recipe):
        """
        Tries to add a recipe to the repository if it does not already exist.

        :param self: This instance of the Repository class.
        :param recipe: The recipe to add.
        :type recipe: Recipe
        """
        if recipe.name in self.data:
            return False  # Recipe already exists.

        self.data[recipe.name] = recipe
        return True

    def save(self):
        """
        Stores the recipes to disk.
        """

        self._write_yaml(
            {name: self._to_dict(recipe) for name, recipe in self.data.items()}
        )

    def delete(self, recipe_name: str):
        """
        Deletes a recipe from the repository.

        :param self: This instance of the Repository class.
        :param recipe_name: The name of the recipe to delete.
        :type recipe_name: str
        """
        if recipe_name in self.data:
            del self.data[recipe_name]
            self.save()

    def get(self, recipe_name: str):
        """
        Gets a recipe by name.

        :param self: This instance of the Repository class.
        :param recipe_name: The name of the recipe to get.
        :return: The recipe if found, otherwise None.
        """
        return self.data.get(recipe_name)

    def get_random_recipe(self, recipe_type: str):
        """
        Gets a random recipe, filtered by type.

        :param self: This instance of the Repository class.
        :param recipe_type: The type of recipe to filter by.
        :type recipe_type: str
        :return: A random recipe.
        :rtype: Recipe
        """

        filtered_recipes = [
            recipe for recipe in self.data.values() if recipe.type == recipe_type
        ]

        if not filtered_recipes:
            return None

        return random.choice(filtered_recipes)

    def _load(self):
        """
        Loads the recipes from disk.
        """
        data = self._read_yaml()

        self.data = {name: self._from_dict(payload) for name, payload in data.items()}

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
            "type": recipe.type,
            "ingredients": [  # yaml does not support tuples
                {"amount": amount, "product": product}
                for amount, product in recipe.ingredients
            ],
            "instructions": recipe.instructions,
            "nutrition": recipe.nutrition,
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
        instance.type = data.get("type", "unknown")
        ingredients = data.get("ingredients", [])
        # Convert dictionary format to tuples (amount, product)
        instance.ingredients = [
            (item["amount"], item["product"]) for item in ingredients
        ]
        instance.instructions = data.get("instructions", "")
        instance.nutrition = data.get("nutrition", {})
        return instance
