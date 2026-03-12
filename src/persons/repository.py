from common.yaml_file_repository import YamlFileRepository
from config.configuration import Configuration
from persons.person import Person


class Repository(YamlFileRepository):
    def __init__(self, configuration: Configuration):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        :param configuration: The configuration object containing the storage path.
        :type configuration: Configuration
        """
        super().__init__(configuration.persons_storage_path, Person)

    def try_add(self, person: Person) -> bool:
        """
        Tries to add a person to the repository if they do not already exist.

        :param self: This instance of the Repository class.
        :param person: The person to add.
        :type person: Person
        :return: True if the person was added, False if they already exist.
        :rtype: bool
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
