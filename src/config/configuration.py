import openfoodfacts
import logging
from pathlib import Path
from dataclasses import dataclass


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Configuration:
    """A dataclass that holds the configuration settings for the application."""

    app_name: str = "Fezzikazza"  # Fat cat in Althochdeutsch.
    version: str = "0.2.0"
    temp_folder: str = "temp"

    # Configuration is hardcoded here for simplicity.
    # TODO: Later, read from a config file or environment variables.

    # OpenFoodFacts API configuration
    openfoodfacts_api_version: openfoodfacts.APIVersion = openfoodfacts.APIVersion.v3

    openfoodfacts_api_environment: openfoodfacts.Environment = (
        openfoodfacts.Environment.org
    )

    openfoodfacts_api_country: openfoodfacts.Country = openfoodfacts.Country.de
    openfoodfacts_api_timeout: int = 15  # seconds

    openfoodfacts_download_url: str = (
        "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
    )

    openfoodfacts_gz_file_name: str = "en.openfoodfacts.org.products.csv.gz"

    # Schweizer Nährwertdatenbank
    swiss_nutrition_db_download_url: str = (
        "https://webapp.prod.blv.foodcase-services.com/wp-content/uploads/2025/07/Schweizer_Nahrwertdatenbank.xlsx"
    )

    swiss_nutrition_xlsx_file_name: str = "Schweizer_Nahrwertdatenbank.xlsx"

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
        """
        Initializes the Configuration object and sets up the necessary folders.

        :param self: The Configuration instance being initialized.
        """
        self.temp_folder = str(PROJECT_ROOT / type(self).temp_folder)
        self.logging_folder = str(PROJECT_ROOT / type(self).logging_folder)
        self.sqlite_data_folder = str(PROJECT_ROOT / type(self).sqlite_data_folder)

        self.sqlite_url = (
            f"sqlite:///{(Path(self.sqlite_data_folder) / 'data.db').as_posix()}"
        )

        # Ensure the logging folder exists.
        Path(self.logging_folder).mkdir(parents=True, exist_ok=True)
        Path(self.sqlite_data_folder).mkdir(parents=True, exist_ok=True)
        Path(self.temp_folder).mkdir(parents=True, exist_ok=True)


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configuration = Configuration()
