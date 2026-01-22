from common.yaml_file_repository import YamlFileRepository
from config import config
from persons.person import Person


class Repository(YamlFileRepository):
    def __init__(self):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        super().__init__(config.persons_storage_path, self._to_dict)

    def try_add(self, person: Person):
        """
        Tries to add a person to the repository if they do not already exist.

        :param self: This instance of the Repository class.
        :param person: The person to add.
        :type person: Person
        """
        if person.name in self.data:
            return False  # Person already exists.

        self.data[person.name] = person
        self.save()
        return True

    def delete(self, name: str):
        """
        Deletes a person from the repository by name.

        :param self: This instance of the Repository class.
        :param name: The name of the person to delete.
        :type name: str
        """
        if name in self.data:
            del self.data[name]
            self.save()

    def _to_dict(self):
        """
        Converts a Person object to a dictionary for serialization.

        :param self: This instance of the Repository class.
        :param person: The Person object to convert.
        :type person: Person
        :return: A dictionary representation of the Person object.
        :rtype: dict
        """
        return {
            name: person.__dict__
            for name, person in self.data.items()  # __dict__ gives the attributes of the object as a dictionary
        }
