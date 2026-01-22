from pathlib import Path
import yaml
from typing import Callable


class YamlFileRepository:
    def __init__(self, storage_path: Path, to_dict: Callable):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        self.data = {}
        self.storage_path = storage_path
        self._ensure_storage_path_exists()
        self._to_dict = to_dict

    def save(self):
        """
        Saves the repository data to the YAML file.

        :param self: This instance of the Repository class.
        """
        self._write_yaml(self._to_dict())

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
