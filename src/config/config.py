import openfoodfacts
import logging
import config.logger as logger_config
from pathlib import Path

app_name = "Fezzikazza"  # Fat cat in Althochdeutsch.
version = "0.1.0"

# Configuration is hardcoded here for simplicity.
# TODO: Later, read from a config file or environment variables.

# OpenFoodFacts API configuration
openfoodfacts_api_version = openfoodfacts.APIVersion.v3
openfoodfacts_api_environment = openfoodfacts.Environment.org
openfoodfacts_api_country = openfoodfacts.Country.de
openfoodfacts_api_timeout = 60  # seconds

# Logging
logging_folder = "logs"
logging_file_name = "app.log"
logging_file_size = 1024 * 1024  # 1 MB
logging_backup_count = 5
logging_encoding = "utf-8"
logging_basic_level = logging.INFO
logging_basic_format = "%(asctime)s | %(levelname)s | %(message)s"

# Recipe storage
recipes_storage_path = Path("data/recipes.yaml")

# Person storage
persons_storage_path = Path("data/persons.yaml")


def configure():
    logger_config.configure()
