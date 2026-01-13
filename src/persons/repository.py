from common.yaml_file_repository import YamlFileRepository
from config import config
from persons.person import Person


class Repository(YamlFileRepository):
    def __init__(self):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        super().__init__(config.persons_storage_path)

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
        self._save()
        return True

    def _save(self):
        """
        Saves the repository data to the YAML file.

        :param self: This instance of the Repository class.
        """
        # Convert Person objects to dictionaries for serialization.
        serializable_data = {
            name: person.__dict__
            for name, person in self.data.items()  # __dict__ gives the attributes of the object as a dictionary
        }

        self._write_yaml(serializable_data)
