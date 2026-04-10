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
    sqlite_file_name: str = "data.db"
    sqlite_file_path: str = f"{sqlite_data_folder}/{sqlite_file_name}"
    sqlite_url: str = f"sqlite:///.//{sqlite_file_path}"
    sqlite_echo: bool = False
    sqlite_auto_flush: bool = False

    models_folder: str = "models"

    embedding_models = {
        "embeddinggemma-300m-GGUF-Q8_0": {
            "repo": "unsloth/embeddinggemma-300m-GGUF",
            "filename": "embeddinggemma-300M-Q8_0.gguf",
        },
        "embeddinggemma-300m-GGUF-Q4_0": {
            "repo": "unsloth/embeddinggemma-300m-GGUF",
            "filename": "embeddinggemma-300m-Q4_0.gguf",
        },
        "nomic-embed-text-v1.5-Q2_K": {
            "repo": "nomic-ai/nomic-embed-text-v1.5-GGUF",
            "filename": "nomic-embed-text-v1.5.Q2_K.gguf",
        },
        "nomic-embed-text-v1.5-Q4_K_S": {
            "repo": "nomic-ai/nomic-embed-text-v1.5-GGUF",
            "filename": "nomic-embed-text-v1.5.Q4_K_S.gguf",
        },
        "bge-small-en-v1.5": {
            "repo": "BAAI/bge-small-en-v1.5",
            "filename": "bge-small-en-v1.5.gguf",
        },
        "bge-micro-en-v1.5": {
            "repo": "BAAI/bge-micro-en-v1.5",
            "filename": "bge-micro-en-v1.5.gguf",
        },
    }

    used_embedding_model = embedding_models["nomic-embed-text-v1.5-Q2_K"]
    embedding_chunk_size: int = 2024
    embedding_chunk_overlap: int = 256
    embedding_threads: int = 8
    embedding_batch_size: int = 10

    def __init__(self):
        """
        Initializes the Configuration object and sets up the necessary folders.

        :param self: The Configuration instance being initialized.
        """
        self.temp_folder = str(PROJECT_ROOT / type(self).temp_folder)
        self.logging_folder = str(PROJECT_ROOT / type(self).logging_folder)
        self.sqlite_data_folder = str(PROJECT_ROOT / type(self).sqlite_data_folder)
        self.sqlite_file_path = str(PROJECT_ROOT / type(self).sqlite_file_path)
        self.sqlite_url = f"sqlite:///{Path(self.sqlite_file_path).as_posix()}"
        self.models_folder = str(PROJECT_ROOT / type(self).models_folder)

        self.used_embedding_model_path = str(
            PROJECT_ROOT
            / type(self).models_folder
            / self.used_embedding_model["filename"]
        )

        # Ensure the logging folder exists.
        Path(self.logging_folder).mkdir(parents=True, exist_ok=True)
        Path(self.sqlite_data_folder).mkdir(parents=True, exist_ok=True)
        Path(self.temp_folder).mkdir(parents=True, exist_ok=True)
        Path(self.models_folder).mkdir(parents=True, exist_ok=True)


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configuration = Configuration()
