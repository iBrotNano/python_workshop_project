from config.configuration import Configuration
from common.terminal.progress_callback import ProgressCallback, emit_progress
from persistence.database_engine import DatabaseEngine
from persistence.modell_downloader import ModellDownloader
from persistence.retriever_manager import retriever_manager
from persistence.sqlite_rag_factory import SQLiteRagFactory
from recipes.repository import RecipeRepository
from sqlite_rag import SQLiteRag


class RecipeEmbeddingIndexer:
    """Adds embeddings for stored recipes to the recipe-only vector database."""

    def __init__(self, configuration: Configuration, database_engine: DatabaseEngine):
        """
        Initializes the indexer with application configuration and persistence.

        :param configuration: Application and embedding model configuration.
        :type configuration: Configuration
        :param database_engine: Database engine used to load stored recipes.
        :type database_engine: DatabaseEngine
        """
        self.__configuration = configuration
        self.__database_engine = database_engine
        self.__sqlite_rag_factory = SQLiteRagFactory(configuration)

    def create_embeddings(
        self, progress_callback: ProgressCallback | None = None
    ) -> dict[str, int]:
        """
        Adds missing stored recipe embeddings without modifying nutrition vectors.

        :param progress_callback: Optional callback receiving progress updates.
        :type progress_callback: ProgressCallback | None
        :return: Counts of newly indexed and already indexed recipes.
        :rtype: dict[str, int]
        """
        retriever_manager.close()

        with self.__database_engine.get_db() as session:
            recipes = RecipeRepository(session).get_all_with_ids()

        rag = self.__sqlite_rag_factory.create_for_recipe_embedding()

        try:
            existing_uris = self.__get_existing_recipe_uris(rag)

            missing_recipes = [
                (recipe_id, recipe)
                for recipe_id, recipe in recipes
                if self.__build_document_uri(recipe_id) not in existing_uris
            ]

            skipped = len(recipes) - len(missing_recipes)

            emit_progress(
                progress_callback,
                phase="create_recipe_embeddings",
                description="Creating recipe embeddings",
                completed=0,
                total=len(missing_recipes),
            )

            if missing_recipes:
                ModellDownloader(self.__configuration).download_model_if_not_exists(
                    self.__configuration.ai_used_embedding_model["repo"],
                    self.__configuration.ai_used_embedding_model["filename"],
                )

            for completed, (recipe_id, recipe) in enumerate(missing_recipes, start=1):
                rag.add_text(
                    recipe.as_markdown(),
                    uri=self.__build_document_uri(recipe_id),
                    metadata={
                        "entity_type": "recipe",
                        "recipe_id": recipe_id,
                    },
                )

                emit_progress(
                    progress_callback,
                    phase="create_recipe_embeddings",
                    description="Creating recipe embeddings",
                    completed=completed,
                    total=len(missing_recipes),
                )

            return {"created": len(missing_recipes), "skipped": skipped}
        finally:
            rag.close()

    def __get_existing_recipe_uris(self, rag: SQLiteRag) -> set[str]:
        """
        Gets recipe document URIs already stored in the recipe vector database.

        :param rag: The SQLiteRag instance containing the recipe documents.
        :type rag: SQLiteRag
        :return: Existing recipe document URIs.
        :rtype: set[str]
        """
        rows = rag._conn.execute(
            "SELECT uri FROM documents WHERE uri LIKE 'recipe:%'"
        ).fetchall()

        return {row["uri"] for row in rows}

    def __build_document_uri(self, recipe_id: int) -> str:
        """
        Builds a stable URI for a recipe vector document.

        :param recipe_id: The relational database identifier of the recipe.
        :type recipe_id: int
        :return: A stable recipe URI.
        :rtype: str
        """
        return f"recipe:{recipe_id}"
