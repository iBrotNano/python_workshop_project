from dataclasses import fields
from sqlalchemy import text
from config.configuration import Configuration
from common.progress_callback import ProgressCallback, emit_progress
from common.sigint_handler import SigintHandler
from persistence.database_engine import DatabaseEngine
from persistence.openfoodfacts_update_pipeline import OpenFoodFactsUpdatePipeline
from nutrition.nutrition import Nutrition
from nutrition.nutrition_repository import NutritionRepository
from sqlite_rag import SQLiteRag
from persistence.modell_downloader import ModellDownloader


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
        self.__configuration = configuration
        self.__database_engine = database_engine

        self.__openfoodfacts_pipeline = OpenFoodFactsUpdatePipeline(
            self.__configuration, database_engine
        )

        # TODO: Implement SwissNutritionDbUpdatePipeline as a second source for nutrition data and use it in this updater.
        # self._swiss_nutrition_xlsx_path = (
        #     Path(self._configuration.temp_folder)
        #     / self._configuration.swiss_nutrition_xlsx_file_name
        # ).resolve()

        # self._swiss_nutrition_csv_path = self._swiss_nutrition_xlsx_path.with_suffix(
        #     ".csv"
        # ).resolve()

    def update(
        self,
        progress_callback: ProgressCallback | None = None,
        embedding_creation_offset: int = 0,
    ) -> dict[str, bool | int]:
        """
        Downloads the Open Food Facts gzip export and extracts the CSV file.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :param embedding_creation_offset: Number of already processed records used to resume embedding creation.
        :type embedding_creation_offset: int
        :return: Update status containing cancellation state and the next resume offset.
        :rtype: dict[str, bool | int]
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
        # TODO: Uncomment the pipeline run.
        # self.__openfoodfacts_pipeline.run(progress_callback)
        return self.__create_embeddings(progress_callback, embedding_creation_offset)

    def __create_embeddings(
        self, progress_callback: ProgressCallback | None = None, offset: int = 0
    ) -> dict[str, bool | int]:
        """
        Creates embeddings for the nutrition data and stores them in the database.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :param offset: Number of already processed records to skip when resuming.
        :type offset: int
        :return: Status containing cancellation state and the next resume offset.
        :rtype: dict[str, bool | int]
        """

        ModellDownloader(self.__configuration).download_model_if_not_exists(
            self.__configuration.ai_used_embedding_model["repo"],
            self.__configuration.ai_used_embedding_model["filename"],
        )

        batch_size = self.__configuration.ai_embedding_batch_size
        processed_records = offset
        sigint_handler = SigintHandler()
        rag: SQLiteRag | None = None

        try:
            with sigint_handler:
                rag = self.__create_clean_rag() if offset == 0 else self.__create_rag()

                with self.__database_engine.get_db() as session:
                    repository = NutritionRepository(session)
                    total = repository.count()

                    emit_progress(
                        progress_callback,
                        phase="create_embeddings",
                        description="Creating embeddings",
                        completed=processed_records,
                        total=total,
                    )

                    for batch in repository.get_batches(batch_size, offset):
                        for nutrition in batch:
                            rag.add_text(
                                self.__build_chunk(nutrition),
                                uri=self.__build_document_uri(nutrition),
                                metadata=self.__build_chunk_metadata(nutrition),
                            )

                        processed_records += len(batch)

                        emit_progress(
                            progress_callback,
                            phase="create_embeddings",
                            description=(
                                "Cancellation requested - finishing current batch"
                                if sigint_handler.is_cancellation_requested
                                else "Creating embeddings"
                            ),
                            completed=processed_records,
                            total=total,
                        )

                        if sigint_handler.is_cancellation_requested:
                            break

            return {
                "cancelled": sigint_handler.is_cancellation_requested,
                "next_offset": processed_records,
            }
        finally:
            if rag is not None:
                rag.close()

    def __create_clean_rag(self) -> SQLiteRag:
        """
        Drops all sqlite-rag tables and recreates the schema.

        :return: A new sqlite-rag instance with a recreated schema.
        :rtype: SQLiteRag
        """

        with self.__database_engine.engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS _sqliteai_vector"))
            connection.execute(text("DROP TABLE IF EXISTS chunks"))
            connection.execute(text("DROP TABLE IF EXISTS chunks_fts"))
            connection.execute(text("DROP TABLE IF EXISTS chunks_fts_config"))
            connection.execute(text("DROP TABLE IF EXISTS chunks_fts_data"))
            connection.execute(text("DROP TABLE IF EXISTS chunks_fts_docsize"))
            connection.execute(text("DROP TABLE IF EXISTS chunks_fts_idx"))
            connection.execute(text("DROP TABLE IF EXISTS documents"))
            connection.execute(text("DROP TABLE IF EXISTS sentences"))
            connection.execute(text("DROP TABLE IF EXISTS settings"))

        return self.__create_rag()

    def __create_rag(self) -> SQLiteRag:
        """
        Creates a sqlite-rag instance with the configured embedding settings.

        :return: An initialized sqlite-rag instance.
        :rtype: SQLiteRag
        """
        return SQLiteRag.create(
            self.__configuration.sqlite_file_path,
            {
                "model_path": self.__configuration.ai_used_embedding_model_path,
                "chunk_size": self.__configuration.ai_embedding_chunk_size,
                "chunk_overlap": self.__configuration.ai_embedding_chunk_overlap,
            },
        )

    def __build_chunk(self, nutrition: Nutrition) -> str:
        """
        Builds an embedding chunk from a nutrition model.

        :param self: This instance of the NutritionDbUpdater class.
        :param nutrition: The nutrition model to convert into a chunk.
        :type nutrition: Nutrition
        :return: The formatted chunk text.
        :rtype: str
        """
        excluded_fields = {"id"}
        lines: list[str] = []

        for field_definition in fields(Nutrition):
            field_name = field_definition.name

            if field_name in excluded_fields:
                continue

            value = getattr(nutrition, field_name)

            if value is None:
                continue

            if isinstance(value, list):
                if not value:
                    continue

                lines.append(f"{field_name}: {'; '.join(str(item) for item in value)}")
                continue

            lines.append(f"{field_name}: {value}")

        return "\n".join(lines)

    def __build_document_uri(self, nutrition: Nutrition) -> str:
        """
        Builds a stable document URI for a nutrition record.

        :param nutrition: The nutrition model the document belongs to.
        :type nutrition: Nutrition
        :return: A stable URI that identifies the nutrition document in sqlite-rag.
        :rtype: str
        """
        return f"nutrition:{nutrition.id}"

    def __build_chunk_metadata(self, nutrition: Nutrition) -> dict[str, int | str]:
        """
        Builds sqlite-rag metadata for a nutrition record.

        :param nutrition: The nutrition model the metadata belongs to.
        :type nutrition: Nutrition
        :return: Metadata used to resolve the source record after retrieval.
        :rtype: dict[str, int | str]
        """
        metadata: dict[str, int | str] = {
            "entity_type": "nutrition",
            "nutrition_id": nutrition.id,
        }

        if nutrition.code:
            metadata["external_code"] = nutrition.code

        if nutrition.url:
            metadata["source_url"] = nutrition.url

        return metadata
