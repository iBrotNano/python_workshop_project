from sqlalchemy.orm import Session
from persons.activity_level import ActivityLevel
from persons.activity_level_entity import ActivityLevelEntity
from persons.person import Person
from persistence.model_registry import load_model_definitions


class ActivityLevelRepository:
    def __init__(self, session: Session):
        """
        Initializes the Repository with the provided SQLAlchemy session.

        :param self: This instance of the Repository class.
        :param session: The SQLAlchemy session instance.
        :type session: Session
        """

        load_model_definitions()
        self._session = session

    def _entity_to_model(self, entity: ActivityLevelEntity) -> ActivityLevel:
        """
        Converts a ActivityLevelEntity instance to a ActivityLevel model instance.

        :param self: This instance of the Repository class.
        :param entity: The ActivityLevelEntity instance to convert.
        :type entity: ActivityLevelEntity
        :return: A ActivityLevel model instance representing the same data as the provided entity.
        :rtype: ActivityLevel
        """
        model_data = {
            key: value
            for key, value in entity.__dict__.items()
            if key in ActivityLevel.__dataclass_fields__
        }

        if entity.persons is not None:
            model_data["persons"] = [
                Person(
                    **{
                        key: value
                        for key, value in p.__dict__.items()
                        if key in Person.__dataclass_fields__
                        and key != "activity_level"
                    }
                )
                for p in entity.persons
                if p is not None
            ]

        return ActivityLevel(**model_data)

    def _model_to_entity(self, model: ActivityLevel) -> ActivityLevelEntity:
        """
        Converts a ActivityLevel model instance to a ActivityLevelEntity instance.

        :param self: This instance of the Repository class.
        :param model: The model to convert.
        :type model: ActivityLevel
        :return: A ActivityLevelEntity entity with the data of the model.
        :rtype: ActivityLevelEntity
        """
        return ActivityLevelEntity(**model.__dict__)

    def get_all(self) -> list[ActivityLevel]:
        """
        Gets all activity levels from the repository.

        :param self: This instance of the Repository class.
        :return: A list of all activity levels in the repository.
        :rtype: list[ActivityLevel]
        """
        return [
            self._entity_to_model(entity)
            for entity in self._session.query(ActivityLevelEntity).all()
        ]
