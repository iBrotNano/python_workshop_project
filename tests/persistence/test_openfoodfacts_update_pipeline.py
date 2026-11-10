import sys
import types
from types import SimpleNamespace

import pandas
from sqlalchemy import create_engine, text

if "openfoodfacts" not in sys.modules:
    openfoodfacts_stub = types.ModuleType("openfoodfacts")
    openfoodfacts_stub.APIVersion = types.SimpleNamespace(v3="v3")
    openfoodfacts_stub.Environment = types.SimpleNamespace(org="org")
    openfoodfacts_stub.Country = types.SimpleNamespace(de="de")
    sys.modules["openfoodfacts"] = openfoodfacts_stub

from persistence.openfoodfacts_update_pipeline import OpenFoodFactsUpdatePipeline


def create_pipeline() -> OpenFoodFactsUpdatePipeline:
    configuration = SimpleNamespace(
        temp_folder=".",
        openfoodfacts_gz_file_name="openfoodfacts.csv.gz",
        openfoodfacts_download_url="https://example.invalid/openfoodfacts.csv.gz",
    )

    database_engine = SimpleNamespace(engine=None)

    return OpenFoodFactsUpdatePipeline(configuration, database_engine)


def test_filter_quality_criteria_keeps_only_rows_matching_all_criteria():
    pipeline = create_pipeline()

    mapped_chunk = pandas.DataFrame(
        [
            {
                "code": "A",
                "name": "Valid Product",
                "brands": ["BrandA"],
                "energy_100g_kj": 100.0,
                "fat_100g": 1.0,
                "carbohydrates_100g": 2.0,
                "sugars_100g": 1.0,
                "proteins_100g": 3.0,
                "salt_100g": 0.1,
            },
            {
                "code": "B",
                "name": None,
                "brands": ["BrandB"],
                "energy_100g_kj": 100.0,
                "fat_100g": 1.0,
                "carbohydrates_100g": 2.0,
                "sugars_100g": 1.0,
                "proteins_100g": 3.0,
                "salt_100g": 0.1,
            },
            {
                "code": "C",
                "name": "No Brands",
                "brands": [],
                "energy_100g_kj": 100.0,
                "fat_100g": 1.0,
                "carbohydrates_100g": 2.0,
                "sugars_100g": 1.0,
                "proteins_100g": 3.0,
                "salt_100g": 0.1,
            },
            {
                "code": "D",
                "name": "Missing Numeric",
                "brands": ["BrandD"],
                "energy_100g_kj": 100.0,
                "fat_100g": 1.0,
                "carbohydrates_100g": 2.0,
                "sugars_100g": 1.0,
                "proteins_100g": None,
                "salt_100g": 0.1,
            },
            {
                "code": "E",
                "name": "All Zero",
                "brands": ["BrandE"],
                "energy_100g_kj": 0.0,
                "fat_100g": 0.0,
                "carbohydrates_100g": 0.0,
                "sugars_100g": 0.0,
                "proteins_100g": 0.0,
                "salt_100g": 0.0,
            },
            {
                "code": None,
                "name": "Missing Code",
                "brands": ["BrandF"],
                "energy_100g_kj": 100.0,
                "fat_100g": 1.0,
                "carbohydrates_100g": 2.0,
                "sugars_100g": 1.0,
                "proteins_100g": 3.0,
                "salt_100g": 0.1,
            },
        ]
    )

    filtered_chunk, stats = (
        pipeline._OpenFoodFactsUpdatePipeline__filter_quality_criteria(mapped_chunk)
    )

    assert len(filtered_chunk.index) == 1
    assert filtered_chunk.iloc[0]["code"] == "A"
    assert stats["missing_required_fields"] == 2
    assert stats["missing_code"] == 1
    assert stats["missing_brands"] == 1
    assert stats["missing_quality_numeric"] == 0
    assert stats["all_quality_numeric_zero"] == 1


def test_remove_duplicate_codes_keep_latest_keeps_latest_and_stable_tie_breaker():
    pipeline = create_pipeline()
    engine = create_engine("sqlite:///:memory:")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE nutrition (
                    id INTEGER PRIMARY KEY,
                    code TEXT,
                    last_modified_timestamp INTEGER,
                    name TEXT,
                    energy_100g_kj REAL,
                    fat_100g REAL,
                    carbohydrates_100g REAL,
                    sugars_100g REAL,
                    proteins_100g REAL,
                    salt_100g REAL
                )
                """
            )
        )

        connection.execute(
            text(
                """
                INSERT INTO nutrition (
                    id, code, last_modified_timestamp, name,
                    energy_100g_kj, fat_100g, carbohydrates_100g,
                    sugars_100g, proteins_100g, salt_100g
                ) VALUES
                    (1, 'A', 100, 'Old A', 1, 1, 1, 1, 1, 1),
                    (2, 'A', 200, 'New A', 1, 1, 1, 1, 1, 1),
                    (3, 'B', 50, 'Old B', 1, 1, 1, 1, 1, 1),
                    (4, 'B', 50, 'New B Same Timestamp', 1, 1, 1, 1, 1, 1),
                    (5, 'C', 300, 'Only C', 1, 1, 1, 1, 1, 1)
                """
            )
        )

        removed_rows = (
            pipeline._OpenFoodFactsUpdatePipeline__remove_duplicate_codes_keep_latest(
                connection
            )
        )

        remaining_rows = connection.execute(
            text("SELECT code, id FROM nutrition ORDER BY code")
        ).fetchall()

    assert removed_rows == 2
    assert remaining_rows == [("A", 2), ("B", 4), ("C", 5)]


def test_map_chunk_reads_last_modified_timestamp_from_last_modified_t():
    pipeline = create_pipeline()

    chunk = pandas.DataFrame(
        {
            "code": ["X1"],
            "product_name": ["Mapped Product"],
            "brands": ["BrandX"],
            "energy-kj_100g": ["10"],
            "fat_100g": ["1"],
            "carbohydrates_100g": ["2"],
            "sugars_100g": ["3"],
            "proteins_100g": ["4"],
            "salt_100g": ["5"],
            "last_modified_t": ["123"],
        }
    )

    mapped_chunk = pipeline._OpenFoodFactsUpdatePipeline__map_chunk_to_nutrition_schema(
        chunk
    )

    assert mapped_chunk.iloc[0]["last_modified_timestamp"] == 123


def test_filter_quality_criteria_handles_missing_numeric_columns_without_key_error():
    pipeline = create_pipeline()

    mapped_chunk = pandas.DataFrame(
        [
            {
                "code": "X",
                "name": "Only Text",
                "brands": ["BrandX"],
            }
        ]
    )

    filtered_chunk, stats = (
        pipeline._OpenFoodFactsUpdatePipeline__filter_quality_criteria(mapped_chunk)
    )

    assert filtered_chunk.empty
    assert stats["missing_required_fields"] == 1
