from sqlalchemy.orm import Session
from nutrition.nutrition import Nutrition
from nutrition.nutrition_entity import NutritionEntity
from persistence.model_registry import load_model_definitions


class NutritionRepository:
    """
    Repository for accessing the nutrition data in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the Repository with the provided SQLAlchemy session.

        :param session: The SQLAlchemy session instance.
        :type session: Session
        """
        load_model_definitions()
        self._session = session

    def _entity_to_model(self, entity: NutritionEntity) -> Nutrition:
        """
        Converts a NutritionEntity instance to a Nutrition model instance.

        :param self: This instance of the Repository class.
        :param entity: The NutritionEntity instance to convert.
        :type entity: NutritionEntity
        :return: The corresponding Nutrition model instance.
        :rtype: Nutrition
        """
        model_data = {
            key: value
            for key, value in entity.__dict__.items()
            if key in Nutrition.__dataclass_fields__
        }

        return Nutrition(**model_data)

    def _model_to_entity(self, model: Nutrition) -> NutritionEntity:
        """
        Converts a Nutrition model instance to a NutritionEntity instance.

        :param self: This instance of the Repository class.
        :param model: The Nutrition model instance to convert.
        :type model: Nutrition
        :return: The corresponding NutritionEntity instance.
        :rtype: NutritionEntity
        """
        entity_data = {
            key: value
            for key, value in model.__dict__.items()
            if key in Nutrition.__dataclass_fields__
        }

        if entity_data.get("id") in (None, 0):
            entity_data.pop("id", None)

        return NutritionEntity(**entity_data)

    def try_add(self, nutrition: Nutrition) -> bool:
        """
        Tries to save new nutrition data.

        :param self: This instance of the Repository class.
        :param nutrition: The nutrition data to store.
        :type person: Person
        :return: True if storing succeeded, otherwise False.
        :rtype: bool
        """
        entity = self._model_to_entity(nutrition)
        self._session.add(entity)

        try:
            self._session.flush()
        except:
            self._session.rollback()
            raise

        return True
