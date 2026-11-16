import logging

from types import TracebackType
from sqlalchemy.orm import Session
from meal_plan.repository import MealPlanRepository
from persistence.database_engine_factory import database_engine
from persons.activity_level_repository import ActivityLevelRepository
from persons.person_repository import PersonRepository
from recipes.repository import RecipeRepository
from config.configuration import configuration
from persistence.recipe_embedding_indexer import RecipeEmbeddingIndexer

log = logging.getLogger(__name__)


class UnitOfWork:
    """
    Coordinates repositories that should share the same database session.
    """

    def __init__(self):
        """
        Initializes the UnitOfWork.

        :param self: This instance of the UnitOfWork class.
        """
        self._db_context = None
        self._session: Session | None = None
        self._recipes: RecipeRepository | None = None
        self._persons: PersonRepository | None = None
        self._activity_levels: ActivityLevelRepository | None = None
        self._meal_plans: MealPlanRepository | None = None

    def __enter__(self) -> "UnitOfWork":
        """
        Opens a shared database session and initializes repositories in a with statement.

        :param self: This instance of the UnitOfWork class.
        :return: The active unit of work.
        :rtype: UnitOfWork
        """
        self._db_context = database_engine.get_db()
        self._session = self._db_context.__enter__()
        self._recipes = RecipeRepository(self._session)
        self._persons = PersonRepository(self._session)
        self._activity_levels = ActivityLevelRepository(self._session)
        self._meal_plans = MealPlanRepository(self._session)
        return self

    @property
    def recipes(self) -> RecipeRepository:
        """
        Gets the recipe repository for the active unit of work.

        :param self: This instance of the UnitOfWork class.
        :return: The recipe repository bound to the current session.
        :rtype: RecipeRepository
        :raises RuntimeError: If the unit of work is not active.
        """
        if self._recipes is None:
            raise RuntimeError("UnitOfWork is not active.")

        return self._recipes

    @property
    def persons(self) -> PersonRepository:
        """
        Gets the person repository for the active unit of work.

        :param self: This instance of the UnitOfWork class.
        :return: The person repository bound to the current session.
        :rtype: PersonRepository
        :raises RuntimeError: If the unit of work is not active.
        """
        if self._persons is None:
            raise RuntimeError("UnitOfWork is not active.")

        return self._persons

    @property
    def activity_levels(self) -> ActivityLevelRepository:
        """
        Gets the activity level repository for the active unit of work.

        :param self: This instance of the UnitOfWork class.
        :return: The activity level repository bound to the current session.
        :rtype: ActivityLevelRepository
        :raises RuntimeError: If the unit of work is not active.
        """
        if self._activity_levels is None:
            raise RuntimeError("UnitOfWork is not active.")

        return self._activity_levels

    @property
    def meal_plans(self) -> MealPlanRepository:
        """
        Gets the meal plan repository for the active unit of work.

        :param self: This instance of the UnitOfWork class.
        :return: The meal plan repository bound to the current session.
        :rtype: MealPlanRepository
        :raises RuntimeError: If the unit of work is not active.
        """
        if self._meal_plans is None:
            raise RuntimeError("UnitOfWork is not active.")

        return self._meal_plans

    def commit(self) -> list[int]:
        """
        Commits the current transaction of the active unit of work.

        :param self: This instance of the UnitOfWork class.
        :return: IDs of saved recipes whose embeddings could not be created.
        :rtype: list[int]
        :raises RuntimeError: If the unit of work is not active.
        """
        if self._session is None:
            raise RuntimeError("UnitOfWork is not active.")

        recipes = self.recipes.get_new_recipes()
        self._session.commit()
        self.recipes.clear_new_recipes()
        failed = []

        if recipes:
            indexer = RecipeEmbeddingIndexer(configuration, database_engine)

            for recipe_id, recipe in recipes:
                try:
                    indexer.create_embedding(recipe_id, recipe)
                except Exception:
                    log.exception(
                        "Recipe %s was saved but its embedding could not be created.",
                        recipe_id,
                    )

                    failed.append(recipe_id)

        return failed

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """
        Closes the shared database session and rolls back on errors when leaving a with statement.

        :param self: This instance of the UnitOfWork class.
        :param exc_type: The exception type if the with block failed.
        :type exc_type: type[BaseException] | None
        :param exc_val: The exception instance if the with block failed.
        :type exc_val: BaseException | None
        :param exc_tb: The traceback if the with block failed.
        :type exc_tb: TracebackType | None
        :return: The result of the underlying context manager exit handling.
        :rtype: bool | None
        """
        if exc_type is not None and self._session is not None:
            self._session.rollback()

        try:
            if self._db_context is None:
                return None

            return self._db_context.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._session = None
            self._recipes = None
            self._persons = None
            self._activity_levels = None
            self._meal_plans = None
            self._db_context = None
