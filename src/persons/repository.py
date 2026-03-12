from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from persons.person import Person
from persons.person_entity import PersonEntity


class Repository:
    """
    Repository class for managing database access related to persons. This class provides methods to add, retrieve, update, and delete person records in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the Repository with the provided SQLAlchemy session.

        :param session: The SQLAlchemy session instance.
        :type session: Session
        """

        self._session = session

    def _entity_to_model(self, entity: PersonEntity) -> Person:
        """
        Converts a PersonEntity instance to a Person model instance.

        :param self: This instance of the Repository class.
        :param entity: The PersonEntity instance to convert.
        :type entity: PersonEntity
        :return: A Person model instance representing the same data as the provided entity.
        :rtype: Person
        """
        model_data = {
            key: value
            for key, value in entity.__dict__.items()
            if key in Person.__dataclass_fields__
        }

        return Person(**model_data)

    def _model_to_entity(self, model: Person) -> PersonEntity:
        """
        Converts a Person model instance to a PersonEntity instance.

        :param self: This instance of the Repository class.
        :param model: The model to convert.
        :type model: Person
        :return: A PersonEntity entity with the data of the model.
        :rtype:
        """
        return PersonEntity(**model.__dict__)

    def try_add(self, person: Person) -> bool:
        """
        Tries to save a new person.

        :param self: This instance of the Repository class.
        :param person: The person to store.
        :type person: Person
        :return: True if storing succeeded, otherwise False.
        :rtype: bool
        """
        entity = self._model_to_entity(person)
        self._session.add(entity)

        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            return False

        return True

    def get_all(self) -> list[Person]:
        """
        Gets all persons from the repository.

        :param self: This instance of the Repository class.
        :return: A list of all persons in the repository.
        :rtype: list[Person]
        """
        return [
            self._entity_to_model(entity)
            for entity in self._session.query(PersonEntity).all()
        ]

    def update(self, person_id: int, person: Person) -> Person:
        """
        Updates an existing person in the repository.

        :param self: This instance of the Repository class.
        :param person_id: The ID of the person to update.
        :type person_id: int
        :param person: The updated person data.
        :type person: Person
        :return: The updated person.
        :rtype: Person
        """

        entity = self._session.get(PersonEntity, person_id)

        if not entity:
            raise ValueError(f"Person with id {person_id} not found")

        for key, value in person.__dict__.items():
            setattr(entity, key, value)

        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_model(entity)

    def delete(self, name: str):
        """
        Deletes a person from the repository by name.

        :param self: This instance of the Repository class.
        :param name: The name of the person to delete.
        :type name: str
        :raises ValueError: If the person with the specified name is not found.
        """

        entity = self._session.query(PersonEntity).filter_by(name=name).first()

        if not entity:
            raise ValueError(f"Person with name {name} not found")

        self._session.delete(entity)
        self._session.commit()
