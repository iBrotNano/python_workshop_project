import json
import logging
import pandas

from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import Connection
from common.gzip_extractor import GzipExtractor
from common.terminal.progress_callback import ProgressCallback
from config.configuration import Configuration
from nutrition.nutrition_entity import NutritionEntity
from persistence.database_engine import DatabaseEngine
from persistence.updata_pipeline_base import UpdatePipelineBase

log = logging.getLogger(__name__)


class OpenFoodFactsUpdatePipeline(UpdatePipelineBase):
    __SCALAR_SOURCE_COLUMNS = {
        "code": ("code",),
        "name": (
            "product_name",
            "abbreviated_product_name",
            "generic_name",
        ),
        "url": ("url",),
        "quantity": ("quantity",),
        "last_modified_timestamp": ("last_modified_t", "last_modified_timestamp"),
        "energy_100g_kj": ("energy-kj_100g", "energy_100g_kj"),
        "vitamin_b3_100g": ("vitamin-b3_100g", "vitamin-pp_100g"),
    }

    __LIST_SOURCE_COLUMNS = {
        "brands": ("brands",),
        "categories": ("categories",),
    }

    __SYNONYM_SOURCE_COLUMNS = ("abbreviated_product_name", "generic_name")

    __NON_NUMERIC_COLUMNS = {
        "code",
        "name",
        "url",
        "brands",
        "synonyms",
        "categories",
        "quantity",
    }

    __TARGET_COLUMNS = tuple(
        column.name
        for column in NutritionEntity.__table__.columns
        if not column.primary_key
    )

    __REQUIRED_COLUMNS = tuple(
        column.name
        for column in NutritionEntity.__table__.columns
        if not column.primary_key and not column.nullable
    )

    __NUMERIC_COLUMNS = tuple(
        column
        for column in __TARGET_COLUMNS
        if column
        not in {
            "code",
            "name",
            "url",
            "brands",
            "synonyms",
            "categories",
            "quantity",
        }
    )

    __JSON_COLUMNS = (
        "brands",
        "synonyms",
        "categories",
    )

    __QUALITY_REQUIRED_NUMERIC_COLUMNS = (
        "energy_100g_kj",
        "fat_100g",
        "carbohydrates_100g",
        "sugars_100g",
        "proteins_100g",
        "salt_100g",
    )

    def __init__(self, configuration: Configuration, database_engine: DatabaseEngine):
        """
        Initializes the OpenFoodFactsUpdatePipeline instance.

        :param configuration: The configuration instance containing settings.
        :type configuration: Configuration
        :param database_engine: The database engine instance for database operations.
        :type database_engine: DatabaseEngine
        """
        super().__init__()
        self._configuration = configuration
        self._database_engine = database_engine

        self._openfoodfacts_gz_path = (
            Path(self._configuration.temp_folder)
            / self._configuration.openfoodfacts_gz_file_name
        ).resolve()

        self._openfoodfacts_csv_path = self._openfoodfacts_gz_path.with_suffix(
            ""
        ).resolve()

    def run(self, progress_callback: ProgressCallback | None = None):
        """
        Runs the OpenFoodFacts update pipeline.

        :param progress_callback: Optional callback for reporting progress.
        :type progress_callback: ProgressCallback | None
        """
        self._download(
            self._openfoodfacts_gz_path,
            self._configuration.openfoodfacts_download_url,
            progress_callback,
        )

        self.__prepare(progress_callback)
        self.__persist(progress_callback)

    def __prepare(self, progress_callback: ProgressCallback | None = None):
        """
        Prepares the OpenFoodFacts data for import by extracting the gzipped CSV file.

        :param progress_callback: Optional callback for reporting progress during preparation.
        :type progress_callback: ProgressCallback | None
        """
        GzipExtractor(
            self._openfoodfacts_gz_path, self._openfoodfacts_csv_path
        ).extract(progress_callback)

    def __persist(self, progress_callback: ProgressCallback | None = None):
        """
        Persists the OpenFoodFacts data into the database.

        :param progress_callback: Optional callback for reporting progress during persistence.
        :type progress_callback: ProgressCallback | None
        """
        # TODO: Implement progress updates for the import phase
        with self._database_engine.engine.begin() as connection:
            self.__clear_nutrition_table(connection)
            self.__store(self._openfoodfacts_csv_path, connection)

    def __clear_nutrition_table(self, connection: Connection):
        """
        Removes all existing nutrition rows before a full re-import.

        :param self: The instance of the OpenFoodFactsUpdatePipeline class.
        :param connection: Open database connection that owns the active transaction.
        :type connection: Connection
        """
        connection.execute(NutritionEntity.__table__.delete())

    def __store(self, csv_path: Path, connection: Connection):
        """
        Imports Open Food Facts data into the nutrition table.

        :param csv_path: Path to the tab-separated Open Food Facts export.
        :type csv_path: Path
        :param connection: Open database connection that owns the active transaction.
        :type connection: Connection
        """
        chunksize = 1_000
        total_read = 0
        total_after_schema_filter = 0
        total_after_quality_filter = 0
        total_imported = 0
        total_skipped_schema = 0
        total_skipped_missing_code = 0
        total_skipped_missing_brands = 0
        total_skipped_missing_quality_numeric = 0
        total_skipped_all_quality_numeric_zero = 0

        for chunk_index, chunk in enumerate(
            pandas.read_csv(
                csv_path,
                chunksize=chunksize,
                delimiter="\t",
                dtype="string",
                on_bad_lines="skip",
            ),
            start=1,
        ):
            total_read += len(chunk.index)
            mapped_chunk = self.__map_chunk_to_nutrition_schema(chunk)
            quality_chunk, chunk_stats = self.__filter_quality_criteria(mapped_chunk)
            total_after_schema_filter += chunk_stats["after_schema_filter"]
            total_after_quality_filter += len(quality_chunk.index)
            total_skipped_schema += chunk_stats["missing_required_fields"]
            total_skipped_missing_code += chunk_stats["missing_code"]
            total_skipped_missing_brands += chunk_stats["missing_brands"]

            total_skipped_missing_quality_numeric += chunk_stats[
                "missing_quality_numeric"
            ]

            total_skipped_all_quality_numeric_zero += chunk_stats[
                "all_quality_numeric_zero"
            ]

            if quality_chunk.empty:
                log.debug(
                    "Chunk %s skipped entirely after quality filtering.", chunk_index
                )
                continue

            persisted_chunk = self.__prepare_chunk_for_persistence(quality_chunk)

            persisted_chunk.to_sql(
                "nutrition",
                connection,
                if_exists="append",
                index=False,
                method="multi",  # Batch-Inserts
            )

            total_imported += len(persisted_chunk.index)

        deduplicated_rows = self.__remove_duplicate_codes_keep_latest(connection)

        log.info(
            "OpenFoodFacts import summary: read=%s, schema_valid=%s, quality_valid=%s, "
            "inserted=%s, deduplicated=%s, dropped_required=%s, dropped_code=%s, "
            "dropped_brands=%s, dropped_quality_numeric=%s, dropped_all_quality_zero=%s",
            total_read,
            total_after_schema_filter,
            total_after_quality_filter,
            total_imported,
            deduplicated_rows,
            total_skipped_schema,
            total_skipped_missing_code,
            total_skipped_missing_brands,
            total_skipped_missing_quality_numeric,
            total_skipped_all_quality_numeric_zero,
        )

    def __map_chunk_to_nutrition_schema(
        self,
        chunk: pandas.DataFrame,
    ) -> pandas.DataFrame:
        """
        Maps a raw Open Food Facts chunk to the nutrition entity schema.

        :param chunk: Raw chunk read from the Open Food Facts TSV export.
        :type chunk: pandas.DataFrame
        :return: A filtered and normalized DataFrame compatible with the nutrition table.
        :rtype: pandas.DataFrame
        """
        mapped_chunk = pandas.DataFrame(index=chunk.index)

        for column_name in self.__TARGET_COLUMNS:
            mapped_chunk[column_name] = pandas.NA

        for target_column in self.__TARGET_COLUMNS:
            if (
                target_column in self.__LIST_SOURCE_COLUMNS
                or target_column == "synonyms"
            ):
                continue

            source_value = self.__first_matching_column_value(
                chunk,
                self.__get_source_candidates(target_column),
            )

            if source_value is not None:
                mapped_chunk[target_column] = source_value

        for target_column, source_columns in self.__LIST_SOURCE_COLUMNS.items():
            source_value = self.__first_matching_column_value(chunk, source_columns)

            if source_value is not None:
                mapped_chunk[target_column] = source_value.apply(
                    self.__split_text_values
                )

        mapped_chunk["synonyms"] = self.__build_synonyms(chunk)

        if "name" in mapped_chunk.columns:
            mapped_chunk["name"] = mapped_chunk["name"].apply(
                self.__normalize_text_value
            )

        if "code" in mapped_chunk.columns:
            mapped_chunk["code"] = mapped_chunk["code"].apply(
                self.__normalize_text_value
            )

        if "url" in mapped_chunk.columns:
            mapped_chunk["url"] = mapped_chunk["url"].apply(self.__normalize_text_value)

        if "quantity" in mapped_chunk.columns:
            mapped_chunk["quantity"] = mapped_chunk["quantity"].apply(
                self.__normalize_text_value
            )

        for target_column in self.__NUMERIC_COLUMNS:
            mapped_chunk[target_column] = pandas.to_numeric(
                mapped_chunk[target_column], errors="coerce"
            )

        return mapped_chunk

    def __filter_quality_criteria(
        self,
        mapped_chunk: pandas.DataFrame,
    ) -> tuple[pandas.DataFrame, dict[str, int]]:
        """
        Applies import quality criteria to mapped nutrition rows.

        :param mapped_chunk: Chunk already transformed to the nutrition schema.
        :type mapped_chunk: pandas.DataFrame
        :return: Filtered chunk and counters for removed rows.
        :rtype: tuple[pandas.DataFrame, dict[str, int]]
        """
        normalized_chunk = mapped_chunk.reindex(
            columns=list(self.__TARGET_COLUMNS), fill_value=None
        )

        after_schema_filter = self.__drop_rows_missing_required_fields(normalized_chunk)

        rows_missing_required_fields = len(mapped_chunk.index) - len(
            after_schema_filter.index
        )

        after_code_filter = after_schema_filter[after_schema_filter["code"].notna()]

        rows_missing_code = len(after_schema_filter.index) - len(
            after_code_filter.index
        )

        after_brands_filter = after_code_filter[
            after_code_filter["brands"].apply(self.__has_non_empty_collection)
        ]

        rows_missing_brands = len(after_code_filter.index) - len(
            after_brands_filter.index
        )

        required_numeric_chunk = after_brands_filter.reindex(
            columns=list(self.__QUALITY_REQUIRED_NUMERIC_COLUMNS), fill_value=None
        )

        after_numeric_presence_filter = after_brands_filter[
            required_numeric_chunk.notna().all(axis=1)
        ]

        rows_missing_quality_numeric = len(after_brands_filter.index) - len(
            after_numeric_presence_filter.index
        )

        quality_numeric_chunk = after_numeric_presence_filter.reindex(
            columns=list(self.__QUALITY_REQUIRED_NUMERIC_COLUMNS), fill_value=None
        )

        quality_numeric_zero_mask = (quality_numeric_chunk == 0.0).all(axis=1)

        after_non_zero_quality_filter = after_numeric_presence_filter[
            ~quality_numeric_zero_mask
        ]

        rows_all_quality_numeric_zero = len(after_numeric_presence_filter.index) - len(
            after_non_zero_quality_filter.index
        )

        return after_non_zero_quality_filter, {
            "after_schema_filter": len(after_schema_filter.index),
            "missing_required_fields": rows_missing_required_fields,
            "missing_code": rows_missing_code,
            "missing_brands": rows_missing_brands,
            "missing_quality_numeric": rows_missing_quality_numeric,
            "all_quality_numeric_zero": rows_all_quality_numeric_zero,
        }

    def __get_source_candidates(self, target_column: str) -> tuple[str, ...]:
        """
        Returns possible source column names for a nutrition target column.

        :param target_column: The destination column name in the nutrition table.
        :type target_column: str
        :return: Candidate source column names from the Open Food Facts export.
        :rtype: tuple[str, ...]
        """
        if target_column in self.__SCALAR_SOURCE_COLUMNS:
            return self.__SCALAR_SOURCE_COLUMNS[target_column]

        if target_column.endswith("_100g"):
            base_name = target_column.removesuffix("_100g")
            hyphenated_name = f"{base_name.replace('_', '-')}_100g"
            return (target_column, hyphenated_name)

        return (target_column,)

    def __first_matching_column_value(
        self,
        chunk: pandas.DataFrame,
        source_columns: tuple[str, ...],
    ) -> pandas.Series | None:
        """
        Returns the first available source column from the raw import chunk.

        :param chunk: Raw chunk read from the import file.
        :type chunk: pandas.DataFrame
        :param source_columns: Candidate column names in priority order.
        :type source_columns: tuple[str, ...]
        :return: The matching Series or None if no candidate exists in the chunk.
        :rtype: pandas.Series | None
        """
        for source_column in source_columns:
            if source_column in chunk.columns:
                return chunk[source_column]

        return None

    def __build_synonyms(self, chunk: pandas.DataFrame) -> pandas.Series:
        """
        Builds the synonyms JSON column from available text variants.

        :param chunk: Raw chunk read from the import file.
        :type chunk: pandas.DataFrame
        :return: Series containing normalized synonym lists or None.
        :rtype: pandas.Series
        """
        source_series = [
            self.__first_matching_column_value(chunk, (column_name,))
            for column_name in self.__SYNONYM_SOURCE_COLUMNS
        ]

        normalized_sources = [
            (
                series
                if series is not None
                else pandas.Series(pandas.NA, index=chunk.index, dtype="object")
            )
            for series in source_series
        ]

        synonym_rows = zip(*normalized_sources)

        return pandas.Series(
            [self.__merge_text_values(values) for values in synonym_rows],
            index=chunk.index,
            dtype="object",
        )

    def __drop_rows_missing_required_fields(
        self,
        mapped_chunk: pandas.DataFrame,
    ) -> pandas.DataFrame:
        """
        Removes rows that do not contain all required nutrition fields.

        :param mapped_chunk: Chunk already transformed to the nutrition schema.
        :type mapped_chunk: pandas.DataFrame
        :return: Rows that satisfy all non-nullable entity fields.
        :rtype: pandas.DataFrame
        """
        cleaned_chunk = mapped_chunk.copy()

        if "name" in cleaned_chunk.columns:
            cleaned_chunk["name"] = cleaned_chunk["name"].replace("", pandas.NA)

        if "code" in cleaned_chunk.columns:
            cleaned_chunk["code"] = cleaned_chunk["code"].replace("", pandas.NA)

        required_columns = [
            column_name
            for column_name in self.__REQUIRED_COLUMNS
            if column_name in cleaned_chunk.columns
        ]

        return cleaned_chunk.dropna(subset=required_columns)

    def __has_non_empty_collection(self, value: object) -> bool:
        """
        Checks if a value is a non-empty list-like collection.

        :param value: Value to check.
        :type value: object
        :return: True if value contains at least one entry.
        :rtype: bool
        """
        if value is None or value is pandas.NA:
            return False

        if isinstance(value, list):
            return len(value) > 0

        return False

    def __prepare_chunk_for_persistence(
        self,
        mapped_chunk: pandas.DataFrame,
    ) -> pandas.DataFrame:
        """
        Serializes list-like JSON columns before writing to SQLite.

        :param mapped_chunk: Mapped and filtered chunk.
        :type mapped_chunk: pandas.DataFrame
        :return: Chunk ready for persistence.
        :rtype: pandas.DataFrame
        """
        persisted_chunk = mapped_chunk.copy()

        for target_column in self.__JSON_COLUMNS:
            persisted_chunk[target_column] = persisted_chunk[target_column].apply(
                self.__serialize_json_value
            )

        return persisted_chunk

    def __remove_duplicate_codes_keep_latest(self, connection: Connection) -> int:
        """
        Removes duplicated nutrition rows and keeps the latest timestamp per code.

        :param connection: Open database connection that owns the active transaction.
        :type connection: Connection
        :return: Number of removed duplicate rows.
        :rtype: int
        """
        rows_before_deduplication = connection.execute(
            text("SELECT COUNT(*) FROM nutrition")
        ).scalar_one()

        connection.execute(
            text(
                """
                DELETE FROM nutrition
                WHERE id IN (
                    SELECT id
                    FROM (
                        SELECT
                            id,
                            ROW_NUMBER() OVER (
                                PARTITION BY code
                                ORDER BY last_modified_timestamp DESC, id DESC
                            ) AS duplicate_rank
                        FROM nutrition
                    ) ranked
                    WHERE ranked.duplicate_rank > 1
                )
                """
            )
        )

        rows_after_deduplication = connection.execute(
            text("SELECT COUNT(*) FROM nutrition")
        ).scalar_one()

        return rows_before_deduplication - rows_after_deduplication

    def __merge_text_values(self, values: tuple[object, ...]) -> list[str] | None:
        """
        Deduplicates multiple text values into a JSON-compatible list.

        :param values: Raw values collected from multiple source columns.
        :type values: tuple[object, ...]
        :return: A list of unique values or None if nothing usable exists.
        :rtype: list[str] | None
        """
        merged_values: list[str] = []

        for value in values:
            normalized_value = self.__normalize_text_value(value)

            if normalized_value is None or normalized_value in merged_values:
                continue

            merged_values.append(normalized_value)

        return merged_values or None

    def __split_text_values(self, value: object) -> list[str] | None:
        """
        Splits a comma-separated text field into a JSON-compatible list.

        :param value: Raw text field from the import file.
        :type value: object
        :return: A list of unique entries or None if the source value is empty.
        :rtype: list[str] | None
        """
        normalized_value = self.__normalize_text_value(value)

        if normalized_value is None:
            return None

        split_values: list[str] = []

        for entry in normalized_value.split(","):
            cleaned_entry = entry.strip()

            if not cleaned_entry or cleaned_entry in split_values:
                continue

            split_values.append(cleaned_entry)

        return split_values or None

    def __normalize_text_value(self, value: object) -> str | None:
        """
        Converts import values to stripped text while preserving missing values.

        :param value: Raw value from the import file.
        :type value: object
        :return: Normalized text or None for empty values.
        :rtype: str | None
        """
        if value is None or value is pandas.NA:
            return None

        normalized_value = str(value).strip()

        if not normalized_value:
            return None

        return normalized_value

    def __serialize_json_value(self, value: object) -> str | None:
        """
        Serializes list-like values for storage in SQLite JSON columns.

        :param value: Raw JSON-compatible value from the mapped import chunk.
        :type value: object
        :return: Serialized JSON text or None for empty values.
        :rtype: str | None
        """
        if value is None or value is pandas.NA:
            return None

        return json.dumps(value, ensure_ascii=False)
