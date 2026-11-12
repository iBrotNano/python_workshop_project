from contextlib import nullcontext
from types import SimpleNamespace
from persistence.recipe_embedding_indexer import RecipeEmbeddingIndexer
from persistence.sqlite_rag_factory import SQLiteRagFactory


class FakeConnection:
    def __init__(self, documents):
        self.documents = documents

    def execute(self, query):
        assert query == "SELECT uri FROM documents WHERE uri LIKE 'recipe:%'"

        return SimpleNamespace(
            fetchall=lambda: [{"uri": document["uri"]} for document in self.documents]
        )


class FakeRag:
    def __init__(self, documents):
        self.documents = documents
        self._conn = FakeConnection(documents)

    def add_text(self, content, uri, metadata):
        self.documents.append({"content": content, "uri": uri, "metadata": metadata})

    def close(self):
        pass


def test_recipe_indexer_adds_only_missing_documents(monkeypatch):
    indexed_documents = [
        {
            "content": "Existing recipe",
            "uri": "recipe:1",
            "metadata": {"entity_type": "recipe", "recipe_id": 1},
        }
    ]

    recipes = [
        (1, SimpleNamespace(as_markdown=lambda: "Existing recipe")),
        (2, SimpleNamespace(as_markdown=lambda: "# New recipe")),
    ]

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeRepository",
        lambda session: SimpleNamespace(get_all_with_ids=lambda: recipes),
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.SQLiteRagFactory.create_for_recipe_embedding",
        lambda factory: FakeRag(indexed_documents),
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda downloader, repo, filename: None,
    )

    closed_retrievers = []

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.retriever_manager",
        SimpleNamespace(close=lambda: closed_retrievers.append(True)),
    )

    engine = SimpleNamespace(get_db=lambda: nullcontext(object()))

    configuration = SimpleNamespace(
        ai_used_embedding_model={"repo": "model-repo", "filename": "model.gguf"}
    )

    result = RecipeEmbeddingIndexer(configuration, engine).create_embeddings()
    assert result == {"created": 1, "skipped": 1}
    assert indexed_documents[0]["uri"] == "recipe:1"

    assert indexed_documents[1] == {
        "content": "# New recipe",
        "uri": "recipe:2",
        "metadata": {"entity_type": "recipe", "recipe_id": 2},
    }

    assert closed_retrievers == [True]


def test_recipe_indexer_is_idempotent(monkeypatch):
    indexed_documents = []
    recipes = [(7, SimpleNamespace(as_markdown=lambda: "# Stored recipe"))]

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.RecipeRepository",
        lambda session: SimpleNamespace(get_all_with_ids=lambda: recipes),
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.SQLiteRagFactory.create_for_recipe_embedding",
        lambda factory: FakeRag(indexed_documents),
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.ModellDownloader.download_model_if_not_exists",
        lambda downloader, repo, filename: None,
    )

    monkeypatch.setattr(
        "persistence.recipe_embedding_indexer.retriever_manager",
        SimpleNamespace(close=lambda: None),
    )

    engine = SimpleNamespace(get_db=lambda: nullcontext(object()))

    configuration = SimpleNamespace(
        ai_used_embedding_model={"repo": "model-repo", "filename": "model.gguf"}
    )

    indexer = RecipeEmbeddingIndexer(configuration, engine)
    first_result = indexer.create_embeddings()
    second_result = indexer.create_embeddings()
    assert first_result == {"created": 1, "skipped": 0}
    assert second_result == {"created": 0, "skipped": 1}
    assert len(indexed_documents) == 1


def test_recipe_embedding_database_is_a_sidecar_to_the_nutrition_database():
    configuration = SimpleNamespace(sqlite_file_path="C:\\data\\nutrition.db")

    assert (
        SQLiteRagFactory(configuration).recipe_database_path
        == "C:\\data\\nutrition_recipes.db"
    )


def test_recipe_embedding_factory_writes_to_sidecar_database(monkeypatch):
    calls = []

    configuration = SimpleNamespace(
        sqlite_file_path="C:\\data\\nutrition.db",
        ai_use_vulcan_llama_backend=False,
        ai_used_embedding_model_path="model.gguf",
        ai_embedding_chunk_size=2024,
        ai_embedding_chunk_overlap=256,
    )

    monkeypatch.setattr(
        "persistence.sqlite_rag_factory.SQLiteRag.create",
        lambda path, **kwargs: calls.append((path, kwargs)) or object(),
    )

    SQLiteRagFactory(configuration).create_for_recipe_embedding()

    assert calls == [
        (
            "C:\\data\\nutrition_recipes.db",
            {
                "settings": {
                    "model_path": "model.gguf",
                    "chunk_size": 2024,
                    "chunk_overlap": 256,
                    "quantize_scan": False,
                }
            },
        )
    ]
