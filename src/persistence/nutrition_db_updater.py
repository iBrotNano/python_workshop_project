from config.configuration import Configuration
from common.progress_callback import ProgressCallback
from persistence.database_engine import DatabaseEngine
from persistence.openfoodfacts_update_pipeline import OpenFoodFactsUpdatePipeline


class NutritionDbUpdater:
    """
    Downloads the Open Food Facts export and extracts it into the temp folder.
    """

    def __init__(self, configuration: Configuration, database_engine: DatabaseEngine):
        """
        Initializes the updater with the configured download and extraction paths.

        :param configuration: Application configuration with temp and download settings.
        :type configuration: Configuration
        :param database_engine: The database engine used for importing records.
        :type database_engine: DatabaseEngine
        """
        self._openfoodfacts_pipeline = OpenFoodFactsUpdatePipeline(
            configuration, database_engine
        )

        # TODO: Implement SwissNutritionDbUpdatePipeline as a second source for nutrition data and use it in this updater.
        # self._swiss_nutrition_xlsx_path = (
        #     Path(self._configuration.temp_folder)
        #     / self._configuration.swiss_nutrition_xlsx_file_name
        # ).resolve()

        # self._swiss_nutrition_csv_path = self._swiss_nutrition_xlsx_path.with_suffix(
        #     ".csv"
        # ).resolve()

    def update(self, progress_callback: ProgressCallback | None = None):
        """
        Downloads the Open Food Facts gzip export and extracts the CSV file.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :raises OSError: If the download or extraction fails.
        """

        # self._download(
        #     self._swiss_nutrition_xlsx_path,
        #     self._configuration.swiss_nutrition_db_download_url,
        #     progress_callback,
        # )

        # SwissNutritionDbXlsxToCsvConverter(
        #     self._swiss_nutrition_xlsx_path, self._swiss_nutrition_csv_path
        # ).convert(progress_callback)
        self._openfoodfacts_pipeline.run(progress_callback)
