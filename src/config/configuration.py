import openfoodfacts
import logging
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Configuration:
    """A dataclass that holds the configuration settings for the application."""

    app_name: str = "Fezzikazza"  # Fat cat in Althochdeutsch.
    version: str = "0.2.0"

    # Configuration is hardcoded here for simplicity.
    # TODO: Later, read from a config file or environment variables.

    # OpenFoodFacts API configuration
    openfoodfacts_api_version: openfoodfacts.APIVersion = openfoodfacts.APIVersion.v3

    openfoodfacts_api_environment: openfoodfacts.Environment = (
        openfoodfacts.Environment.org
    )

    openfoodfacts_api_country: openfoodfacts.Country = openfoodfacts.Country.de
    openfoodfacts_api_timeout: int = 60  # seconds

    # Logging
    logging_folder: str = "logs"
    logging_file_name: str = "app.log"
    logging_file_size: int = 1024 * 1024  # 1 MB
    logging_backup_count: int = 5
    logging_encoding: str = "utf-8"
    logging_basic_level: int = logging.INFO
    logging_basic_format: str = "%(asctime)s | %(levelname)s | %(message)s"

    # Recipe storage
    recipes_storage_path: Path = Path("data/recipes.yaml")

    # Person storage
    persons_storage_path: Path = Path("data/persons.yaml")


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configuration = Configuration()
