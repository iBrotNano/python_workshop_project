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
        super().__init__(config.recipes_storage_path, Recipe)

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

    def get_random_recipe_by(
        self, recipe_type: str, assigned: set[str] | None = None
    ) -> Recipe | None:
        """
        Gets a random recipe, filtered by type.

        Already  assigned recipes are only returned if there are no not assigned recipes available for the given type.

        :param self: This instance of the Repository class.
        :param recipe_type: The type of recipe to filter by.
        :type recipe_type: str
        :param assigned: A set of recipe names that have already been assigned.
        :type assigned: set[str] | None
        :return: A random recipe if found, otherwise None.
        :rtype: Recipe | None
        """

        filtered_by_type = [
            recipe for recipe in self.data.values() if recipe.type == recipe_type
        ]

        if not filtered_by_type:
            return None

        filtered_by_assigned = []

        if assigned:
            filtered_by_assigned = [
                recipe for recipe in filtered_by_type if recipe.name not in assigned
            ]

        return random.choice(
            filtered_by_assigned if filtered_by_assigned else filtered_by_type
        )
