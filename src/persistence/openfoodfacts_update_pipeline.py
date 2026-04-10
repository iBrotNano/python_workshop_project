import json
import pandas

from pathlib import Path
from sqlalchemy.engine import Connection
from common.gzip_extractor import GzipExtractor
from common.progress_callback import ProgressCallback
from config.configuration import Configuration
from nutrition.nutrition_entity import NutritionEntity
from persistence.database_engine import DatabaseEngine
from persistence.updata_pipeline_base import UpdatePipelineBase


class OpenFoodFactsUpdatePipeline(UpdatePipelineBase):
    _SCALAR_SOURCE_COLUMNS = {
        "code": ("code",),
        "name": (
            "product_name",
            "abbreviated_product_name",
            "generic_name",
        ),
        "url": ("url",),
        "quantity": ("quantity",),
        "energy_100g_kj": ("energy-kj_100g", "energy_100g_kj"),
        "vitamin_b3_100g": ("vitamin-b3_100g", "vitamin-pp_100g"),
    }

    _LIST_SOURCE_COLUMNS = {
        "brands": ("brands",),
        "categories": ("categories",),
    }

    _SYNONYM_SOURCE_COLUMNS = ("abbreviated_product_name", "generic_name")

    _NON_NUMERIC_COLUMNS = {
        "code",
        "name",
        "url",
        "brands",
        "synonyms",
        "categories",
        "quantity",
    }

    _TARGET_COLUMNS = tuple(
        column.name
        for column in NutritionEntity.__table__.columns
        if not column.primary_key
    )

    _REQUIRED_COLUMNS = tuple(
        column.name
        for column in NutritionEntity.__table__.columns
        if not column.primary_key and not column.nullable
    )

    _NUMERIC_COLUMNS = tuple(
        column
        for column in _TARGET_COLUMNS
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

    _JSON_COLUMNS = (
        "brands",
        "synonyms",
        "categories",
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

        self._prepare(progress_callback)
        self._persist(progress_callback)

    def _prepare(self, progress_callback: ProgressCallback | None = None):
        """
        Prepares the OpenFoodFacts data for import by extracting the gzipped CSV file.

        :param progress_callback: Optional callback for reporting progress during preparation.
        :type progress_callback: ProgressCallback | None
        """
        GzipExtractor(
            self._openfoodfacts_gz_path, self._openfoodfacts_csv_path
        ).extract(progress_callback)

    def _persist(self, progress_callback: ProgressCallback | None = None):
        """
        Persists the OpenFoodFacts data into the database.

        :param progress_callback: Optional callback for reporting progress during persistence.
        :type progress_callback: ProgressCallback | None
        """
        # TODO: Implement progress updates for the import phase
        with self._database_engine.engine.begin() as connection:
            self._clear_nutrition_table(connection)
            self._store(self._openfoodfacts_csv_path, connection)

    def _clear_nutrition_table(self, connection: Connection):
        """
        Removes all existing nutrition rows before a full re-import.

        :param self: The instance of the OpenFoodFactsUpdatePipeline class.
        :param connection: Open database connection that owns the active transaction.
        :type connection: Connection
        """
        connection.execute(NutritionEntity.__table__.delete())

    def _store(self, csv_path: Path, connection: Connection):
        """
        Imports Open Food Facts data into the nutrition table.

        :param csv_path: Path to the tab-separated Open Food Facts export.
        :type csv_path: Path
        :param connection: Open database connection that owns the active transaction.
        :type connection: Connection
        """
        chunksize = 1_000
        total_imported = 0
        total_skipped = 0

        for chunk_number, chunk in enumerate(
            pandas.read_csv(
                csv_path,
                chunksize=chunksize,
                delimiter="\t",
                dtype="string",
                on_bad_lines="skip",
            ),
            start=1,
        ):
            mapped_chunk = self._map_chunk_to_nutrition_schema(chunk)
            skipped_rows = len(chunk.index) - len(mapped_chunk.index)
            total_skipped += skipped_rows

            mapped_chunk.to_sql(
                "nutrition",
                connection,
                if_exists="append",
                index=False,
                method="multi",  # Batch-Inserts
            )

            total_imported += len(mapped_chunk.index)

    def _map_chunk_to_nutrition_schema(
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

        for column_name in self._TARGET_COLUMNS:
            mapped_chunk[column_name] = pandas.NA

        for target_column in self._TARGET_COLUMNS:
            if (
                target_column in self._LIST_SOURCE_COLUMNS
                or target_column == "synonyms"
            ):
                continue

            source_value = self._first_matching_column_value(
                chunk,
                self._get_source_candidates(target_column),
            )

            if source_value is not None:
                mapped_chunk[target_column] = source_value

        for target_column, source_columns in self._LIST_SOURCE_COLUMNS.items():
            source_value = self._first_matching_column_value(chunk, source_columns)

            if source_value is not None:
                mapped_chunk[target_column] = source_value.apply(
                    self._split_text_values
                )

        mapped_chunk["synonyms"] = self._build_synonyms(chunk)

        if "name" in mapped_chunk.columns:
            mapped_chunk["name"] = mapped_chunk["name"].apply(
                self._normalize_text_value
            )

        if "code" in mapped_chunk.columns:
            mapped_chunk["code"] = mapped_chunk["code"].apply(
                self._normalize_text_value
            )

        if "url" in mapped_chunk.columns:
            mapped_chunk["url"] = mapped_chunk["url"].apply(self._normalize_text_value)

        if "quantity" in mapped_chunk.columns:
            mapped_chunk["quantity"] = mapped_chunk["quantity"].apply(
                self._normalize_text_value
            )

        for target_column in self._NUMERIC_COLUMNS:
            mapped_chunk[target_column] = pandas.to_numeric(
                mapped_chunk[target_column], errors="coerce"
            )

        for target_column in self._JSON_COLUMNS:
            mapped_chunk[target_column] = mapped_chunk[target_column].apply(
                self._serialize_json_value
            )

        return self._drop_rows_missing_required_fields(mapped_chunk)

    def _get_source_candidates(self, target_column: str) -> tuple[str, ...]:
        """
        Returns possible source column names for a nutrition target column.

        :param target_column: The destination column name in the nutrition table.
        :type target_column: str
        :return: Candidate source column names from the Open Food Facts export.
        :rtype: tuple[str, ...]
        """
        if target_column in self._SCALAR_SOURCE_COLUMNS:
            return self._SCALAR_SOURCE_COLUMNS[target_column]

        if target_column.endswith("_100g"):
            base_name = target_column.removesuffix("_100g")
            hyphenated_name = f"{base_name.replace('_', '-')}_100g"
            return (target_column, hyphenated_name)

        return (target_column,)

    def _first_matching_column_value(
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

    def _build_synonyms(self, chunk: pandas.DataFrame) -> pandas.Series:
        """
        Builds the synonyms JSON column from available text variants.

        :param chunk: Raw chunk read from the import file.
        :type chunk: pandas.DataFrame
        :return: Series containing normalized synonym lists or None.
        :rtype: pandas.Series
        """
        source_series = [
            self._first_matching_column_value(chunk, (column_name,))
            for column_name in self._SYNONYM_SOURCE_COLUMNS
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
            [self._merge_text_values(values) for values in synonym_rows],
            index=chunk.index,
            dtype="object",
        )

    def _drop_rows_missing_required_fields(
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

        cleaned_chunk["name"] = cleaned_chunk["name"].replace("", pandas.NA)

        return cleaned_chunk.dropna(subset=list(self._REQUIRED_COLUMNS))

    def _merge_text_values(self, values: tuple[object, ...]) -> list[str] | None:
        """
        Deduplicates multiple text values into a JSON-compatible list.

        :param values: Raw values collected from multiple source columns.
        :type values: tuple[object, ...]
        :return: A list of unique values or None if nothing usable exists.
        :rtype: list[str] | None
        """
        merged_values: list[str] = []

        for value in values:
            normalized_value = self._normalize_text_value(value)

            if normalized_value is None or normalized_value in merged_values:
                continue

            merged_values.append(normalized_value)

        return merged_values or None

    def _split_text_values(self, value: object) -> list[str] | None:
        """
        Splits a comma-separated text field into a JSON-compatible list.

        :param value: Raw text field from the import file.
        :type value: object
        :return: A list of unique entries or None if the source value is empty.
        :rtype: list[str] | None
        """
        normalized_value = self._normalize_text_value(value)

        if normalized_value is None:
            return None

        split_values: list[str] = []

        for entry in normalized_value.split(","):
            cleaned_entry = entry.strip()

            if not cleaned_entry or cleaned_entry in split_values:
                continue

            split_values.append(cleaned_entry)

        return split_values or None

    def _normalize_text_value(self, value: object) -> str | None:
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

    def _serialize_json_value(self, value: object) -> str | None:
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
