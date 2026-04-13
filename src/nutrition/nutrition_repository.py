from collections.abc import Generator
from sqlalchemy.orm import Session
from nutrition.nutrition import Nutrition
from nutrition.nutrition_entity import NutritionEntity
from persistence.db_schema_registry import load_db_schema_definitions


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
        load_db_schema_definitions()
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
        :type nutrition: Nutrition
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

    def get_batches(
        self, batch_size: int = 500
    ) -> Generator[list[Nutrition], None, None]:
        """
        Gets nutrition records in stable batches.

        :param self: This instance of the Repository class.
        :param batch_size: The maximum number of records per batch.
        :type batch_size: int
        :return: A generator yielding batches of nutrition records.
        :rtype: Generator[list[Nutrition], None, None]
        """
        offset = 0

        while True:
            entities = (
                self._session.query(NutritionEntity)
                .order_by(NutritionEntity.id)
                .offset(offset)
                .limit(batch_size)
                .all()
            )

            if not entities:
                break

            yield [self._entity_to_model(entity) for entity in entities]
            offset += batch_size

    def count(self) -> int:
        """
        Counts the total number of nutrition records in the database.

        :param self: This instance of the Repository class.
        :return: The total count of nutrition records.
        :rtype: int
        """

        return self._session.query(NutritionEntity).count()
