from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from sqlite_rag.models.document import Document
from sqlite_rag.models.document_result import DocumentResult

from nutrition.command_line_handler import CommandLineHandler
from nutrition.nutrition import Nutrition


def create_result(nutrition_id):
    return DocumentResult(
        document=Document(metadata={"entity_type": "nutrition", "nutrition_id": nutrition_id}),
        chunk_id=1,
        combined_rank=1.0,
    )


def test_search_results_resolve_nutrition_records_in_retrieval_order(monkeypatch):
    records = {1: Nutrition(id=1, name="First"), 2: Nutrition(id=2, name="Second")}
    session = object()
    monkeypatch.setattr(
        "nutrition.command_line_handler.database_engine",
        SimpleNamespace(get_db=lambda: nullcontext(session)),
    )
    repository = SimpleNamespace(get_by_ids=lambda ids: records)
    monkeypatch.setattr(
        "nutrition.command_line_handler.NutritionRepository", lambda value: repository
    )

    products = CommandLineHandler()._CommandLineHandler__resolve_results(
        [create_result(2), create_result(1), create_result(2)]
    )

    assert [product.id for product in products] == [2, 1, 2]


@pytest.mark.parametrize("nutrition_id", [None, "1", 0, True])
def test_search_results_reject_invalid_nutrition_metadata(nutrition_id):
    with pytest.raises(ValueError, match="nutrition"):
        CommandLineHandler()._CommandLineHandler__resolve_results(
            [create_result(nutrition_id)]
        )


@pytest.mark.parametrize("metadata", [None, [], {"entity_type": "recipe", "nutrition_id": 1}])
def test_search_results_reject_invalid_metadata_shape(metadata):
    result = create_result(1)
    result.document.metadata = metadata

    with pytest.raises(ValueError, match="nutrition"):
        CommandLineHandler()._CommandLineHandler__resolve_results([result])


def test_search_results_report_missing_nutrition_records(monkeypatch):
    monkeypatch.setattr(
        "nutrition.command_line_handler.database_engine",
        SimpleNamespace(get_db=lambda: nullcontext(object())),
    )
    monkeypatch.setattr(
        "nutrition.command_line_handler.NutritionRepository",
        lambda value: SimpleNamespace(get_by_ids=lambda ids: {}),
    )

    with pytest.raises(LookupError, match="nutrition"):
        CommandLineHandler()._CommandLineHandler__resolve_results([create_result(1)])


def test_search_displays_resolved_products_in_ranked_order(monkeypatch):
    results = [create_result(2), create_result(1)]
    products = {
        1: Nutrition(id=1, name="First"),
        2: Nutrition(id=2, name="Second"),
    }
    monkeypatch.setattr(
        "nutrition.command_line_handler.retriever_manager",
        SimpleNamespace(
            get=lambda config: SimpleNamespace(retrieve=lambda query, top_k: results)
        ),
    )
    monkeypatch.setattr(
        "nutrition.command_line_handler.database_engine",
        SimpleNamespace(get_db=lambda: nullcontext(object())),
    )
    monkeypatch.setattr(
        "nutrition.command_line_handler.NutritionRepository",
        lambda value: SimpleNamespace(get_by_ids=lambda ids: products),
    )
    displayed = []

    def select(message, choices):
        displayed.extend(choice.value for choice in choices)
        return choices[1].value

    monkeypatch.setattr(
        "nutrition.command_line_handler.terminal",
        SimpleNamespace(
            console=SimpleNamespace(status=lambda *args, **kwargs: nullcontext()),
            print_info=lambda message: None,
            print_rule_separated=lambda message: None,
            safe_select=select,
        ),
    )

    selected = CommandLineHandler()._execute_search("apple")

    assert selected is products[2]
    assert displayed[1:] == [products[2], products[1]]
