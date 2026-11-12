from types import SimpleNamespace
from assistant.prompt import Prompt


def test_prompt_exposes_nutrition_and_recipe_retrieval_tools():
    prompt = Prompt(SimpleNamespace())

    tool_names = [
        tool["function"]["name"] for tool in prompt._Prompt__get_tool_definitions()
    ]

    assert tool_names == ["retrieve_nutrition_data", "retrieve_recipe_data"]


def test_recipe_tool_retrieves_from_recipe_database(monkeypatch, tmp_path):
    configuration = SimpleNamespace(sqlite_file_path=str(tmp_path / "nutrition.db"))
    recipe_database_path = tmp_path / "nutrition_recipes.db"
    recipe_database_path.touch()

    result = SimpleNamespace(
        document=SimpleNamespace(content="# Pancakes", metadata={"recipe_id": 3})
    )

    calls = []

    retriever = SimpleNamespace(
        retrieve=lambda query, top_k: calls.append((query, top_k)) or [result]
    )

    monkeypatch.setattr(
        "assistant.prompt.retriever_manager",
        SimpleNamespace(
            get=lambda config, database_path=None: calls.append(database_path)
            or retriever
        ),
    )

    prompt = Prompt(configuration)

    tool_call = {
        "function": {
            "name": "retrieve_recipe_data",
            "arguments": {"query": "pancakes", "top_k": 4},
        }
    }

    response = prompt._Prompt__execute_tool_call(tool_call)

    assert calls == [
        str(recipe_database_path),
        ("pancakes", 4),
    ]

    assert response["results"] == "Result 1:\n# Pancakes"


def test_recipe_tool_reports_missing_recipe_embeddings(tmp_path):
    prompt = Prompt(SimpleNamespace(sqlite_file_path=str(tmp_path / "nutrition.db")))

    tool_call = {
        "function": {
            "name": "retrieve_recipe_data",
            "arguments": {"query": "pancakes"},
        }
    }

    response = prompt._Prompt__execute_tool_call(tool_call)
    assert "error" in response
    assert "create embeddings for stored recipes" in response["error"]


def test_nutrition_tool_keeps_using_main_database(monkeypatch):
    configuration = SimpleNamespace(sqlite_file_path="nutrition.db")
    calls = []
    retriever = SimpleNamespace(retrieve=lambda query, top_k: [])

    monkeypatch.setattr(
        "assistant.prompt.retriever_manager",
        SimpleNamespace(
            get=lambda config, database_path=None: calls.append(database_path)
            or retriever
        ),
    )

    prompt = Prompt(configuration)

    tool_call = {
        "function": {
            "name": "retrieve_nutrition_data",
            "arguments": {"query": "apples"},
        }
    }

    response = prompt._Prompt__execute_tool_call(tool_call)
    assert calls == [None]
    assert response["results"] == "No matching nutrition results were found."
