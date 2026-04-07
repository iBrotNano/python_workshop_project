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
    openfoodfacts_api_timeout: int = 15  # seconds

    # Logging
    logging_folder: str = "logs"
    logging_file_name: str = "app.log"
    logging_file_size: int = 1024 * 1024  # 1 MB
    logging_backup_count: int = 5
    logging_encoding: str = "utf-8"
    logging_basic_level: int = logging.INFO
    logging_basic_format: str = "%(asctime)s | %(levelname)s | %(message)s"

    sqlite_data_folder: str = "data"
    sqlite_url: str = f"sqlite:///.//{sqlite_data_folder}/data.db"
    sqlite_echo: bool = False
    sqlite_auto_flush: bool = False

    def __init__(self):
        # Ensure the logging folder exists.
        Path(self.logging_folder).mkdir(parents=True, exist_ok=True)
        Path(self.sqlite_data_folder).mkdir(parents=True, exist_ok=True)


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configuration = Configuration()
