import yaml

from pathlib import Path
from enum import Enum
from typing import Any


class YamlFileRepository:
    """
    A base class for repositories that store data in YAML files. It provides methods for loading and saving data, as well as converting between objects and dictionaries for serialization.
    """

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

    def _write_yaml(self, obj: Any):
        """
        Writes the given object as YAML to disk.

        :param self: This instance of the Repository class.
        :param obj: The object to write as YAML.
        :type obj: Any
        """
        with open(self.storage_path.absolute(), "w", encoding="utf-8") as file:
            yaml.safe_dump(
                obj,
                file,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

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

    def _to_dict(self) -> dict:
        """
        Converts an object to a dictionary for serialization.

        :param self: This instance of the Repository class.
        :return: A dictionary representation of the Person object.
        :rtype: dict
        """

        return {
            name: self._to_primitive(instance.__dict__)
            for name, instance in self.data.items()
        }

    def _to_primitive(self, value: Any) -> Any:
        """
        Converts values to YAML-safe primitive structures.

        :param value: The value to normalize.
        :return: A normalized primitive value.
        """
        if isinstance(value, Enum):
            return value.value

        if isinstance(value, dict):
            return {
                self._to_primitive(key): self._to_primitive(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self._to_primitive(item) for item in value]

        if isinstance(value, tuple):
            return [self._to_primitive(item) for item in value]

        return value

    def _from_data(self, data: dict) -> dict:
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
