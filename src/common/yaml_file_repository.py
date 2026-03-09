from pathlib import Path
import yaml
from typing import Callable


class YamlFileRepository:
    def __init__(
        self,
        storage_path: Path,
        entity_type: type,
    ):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        :param entity_type: The type of entity to create when deserializing.
        """
        self.data = {}
        self.storage_path = storage_path
        self._entity_type = entity_type
        self._ensure_storage_path_exists()
        self._load()

    def save(self):
        """
        Saves the repository data to the YAML file.

        :param self: This instance of the Repository class.
        """
        self._write_yaml(self._to_dict())

    def _load(self):
        """
        Loads the recipes from disk.
        """
        self.data = self._from_data(self._read_yaml())

    def _ensure_storage_path_exists(self):
        """
        Ensures the storage directory exists.
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_yaml(self, obj):
        """
        Writes the given object as YAML to disk.

        :param self: This instance of the Repository class.
        :param obj: The object to write as YAML.
        :type obj: Any
        """
        with open(self.storage_path.absolute(), "w", encoding="utf-8") as file:
            yaml.dump(obj, file, default_flow_style=False, allow_unicode=True)

    def _read_yaml(self):
        """
        Reads the YAML data from disk.

        :param self: This instance of the Repository class.
        :return: The YAML data read from disk.
        """

        if not self.storage_path.exists():
            return {}

        with open(self.storage_path.absolute(), "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def _to_dict(self):
        """
        Converts an object to a dictionary for serialization.

        :param self: This instance of the Repository class.
        :return: A dictionary representation of the Person object.
        :rtype: dict
        """
        return {name: instance.__dict__ for name, instance in self.data.items()}

    def _from_data(self, data: dict):
        """
        Converts a dictionary to entity objects for deserialization.

        :param self: This instance of the Repository class.
        :param data: The dictionary to convert.
        :type data: dict
        :return: A dictionary of entity objects.
        :rtype: dict
        """
        return {
            name: self._entity_type(
                **payload
            )  # Unpack the dictionary to create an entity object
            for name, payload in data.items()
        }
