import random

from recipes.recipe import Recipe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from recipes.recipe_entity import RecipeEntity


class Repository:
    """
    Repository for accessing the recipes in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the Repository with the provided SQLAlchemy session.

        :param session: The SQLAlchemy session instance.
        :type session: Session
        """
        self._session = session

    def _entity_to_model(self, entity: RecipeEntity) -> Recipe:
        """
        Converts a RecipeEntity instance to a Recipe model instance.

        :param self: This instance of the Repository class.
        :param entity: The RecipeEntity instance to convert.
        :type entity: RecipeEntity
        :return: The corresponding Recipe model instance.
        :rtype: Recipe
        """
        model_data = {
            key: value
            for key, value in entity.__dict__.items()
            if key in Recipe.__dataclass_fields__
        }

        return Recipe(**model_data)

    def _model_to_entity(self, model: Recipe) -> RecipeEntity:
        """
        Converts a Recipe model instance to a RecipeEntity instance.

        :param self: This instance of the Repository class.
        :param model: The Recipe model instance to convert.
        :type model: Recipe
        :return: The corresponding RecipeEntity instance.
        :rtype: RecipeEntity
        """
        return RecipeEntity(**model.__dict__)

    def try_add(self, recipe: Recipe):
        """
        Tries to add a recipe to the repository if it does not already exist.

        :param self: This instance of the Repository class.
        :param recipe: The recipe to add.
        :type recipe: Recipe
        """

        entity = self._model_to_entity(recipe)
        self._session.add(entity)

        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            return False

        return True

    def delete(self, recipe_name: str):
        """
        Deletes a recipe from the repository.

        :param self: This instance of the Repository class.
        :param recipe_name: The name of the recipe to delete.
        :type recipe_name: str
        """

        entity = self._session.query(RecipeEntity).filter_by(name=recipe_name).first()

        if not entity:
            raise ValueError(f"Recipe with name {recipe_name} not found")

        self._session.delete(entity)
        self._session.commit()

    def get(self, recipe_name: str) -> Recipe | None:
        """
        Gets a recipe by name.

        :param self: This instance of the Repository class.
        :param recipe_name: The name of the recipe to get.
        :type recipe_name: str
        :return: The recipe if found, otherwise None.
        :rtype: Recipe | None
        """
        entity = self._session.query(RecipeEntity).filter_by(name=recipe_name).first()

        if not entity:
            return None

        return self._entity_to_model(entity)

    def get_all(self) -> list[Recipe]:
        """
        Gets all recipes in the repository.

        :param self: This instance of the Repository class.
        :return: A list of all recipes in the repository.
        :rtype: list[Recipe]
        """
        return [
            self._entity_to_model(entity)
            for entity in self._session.query(RecipeEntity).all()
        ]

    def get_random_recipe_by(
        self, recipe_type: str, assigned: set[str] | None = None
    ) -> Recipe | None:
        """
        Gets a random recipe, filtered by type.

        Already assigned recipes are only returned if there are no not assigned recipes available for the given type.

        :param self: This instance of the Repository class.
        :param recipe_type: The type of recipe to filter by.
        :type recipe_type: str
        :param assigned: A set of recipe names that have already been assigned.
        :type assigned: set[str] | None
        :return: A random recipe if found, otherwise None.
        :rtype: Recipe | None
        """

        filtered_by_type = [
            recipe for recipe in self.get_all() if recipe.type == recipe_type
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
