import logging
import questionary

from sqlalchemy.exc import SQLAlchemyError
from common.terminal.console_logging_suppressor import suppress_console_logging
from common.terminal.progress import Progress
from common.terminal.terminal import terminal
from config.configuration import configuration
from persistence.database_engine_factory import database_engine
from persistence.database_maintenance import DatabaseMaintenance
from persistence.nutrition_db_updater import NutritionDbUpdater
from persistence.retriever_manager import retriever_manager
from recipes.recipe_embedding_cleanup import RecipeEmbeddingCleanup
from recipes.recipe_embedding_indexer import RecipeEmbeddingIndexer

from common.terminal.input_validators import (
    non_negative_integer_and_and_configured_negative_values_or_empty,
)

log = logging.getLogger(__name__)


class CommandLineHandler:
    """
    Handles the command line menus for application settings.
    """

    CANCEL_COMMAND = "CANCEL"
    MANAGE_DATABASE_COMMAND = "MANAGE_DATABASE"
    UPDATE_DATABASE_COMMAND = "UPDATE_DATABASE"
    COMPACT_DATABASE_COMMAND = "COMPACT_DATABASE"
    CREATE_EMBEDDINGS_COMMAND = "CREATE_EMBEDDINGS"
    CLEANUP_EMBEDDINGS_COMMAND = "CLEANUP_EMBEDDINGS"

    def __init__(self):
        """
        Initializes the settings command line handler.
        """
        self.__updater = NutritionDbUpdater(configuration, database_engine)

    def show(self):
        """
        Displays the settings menu and handles its selection.
        """
        while True:
            command = self._get_settings_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return

            if command == self.MANAGE_DATABASE_COMMAND:
                self._show_database_menu()

    def _get_settings_menu_selection(self):
        """
        Displays the settings menu and gets the user's selection.

        :return: The command selected by the user.
        """
        choices = [
            questionary.Choice(
                "Database",
                value=self.MANAGE_DATABASE_COMMAND,
            ),
            questionary.Choice(
                "Back to main menu",
                value=self.CANCEL_COMMAND,
            ),
        ]

        return terminal.safe_select("What settings do you want to manage?", choices)

    def _show_database_menu(self):
        """
        Displays the database menu and executes maintenance selections.
        """
        while True:
            command = self._get_database_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return

            if command == self.UPDATE_DATABASE_COMMAND:
                self._update_database()

            if command == self.COMPACT_DATABASE_COMMAND:
                self._compact_database()

            if command == self.CREATE_EMBEDDINGS_COMMAND:
                self._create_recipe_embeddings()

            if command == self.CLEANUP_EMBEDDINGS_COMMAND:
                self._cleanup_recipe_embeddings()

    def _get_database_menu_selection(self):
        """
        Displays the database menu and gets the user's selection.

        :return: The command selected by the user.
        """
        choices = [
            questionary.Choice(
                "Update the database",
                value=self.UPDATE_DATABASE_COMMAND,
            ),
            questionary.Choice(
                "Compact the database",
                value=self.COMPACT_DATABASE_COMMAND,
            ),
            questionary.Choice(
                "Create embeddings for stored recipes",
                value=self.CREATE_EMBEDDINGS_COMMAND,
            ),
            questionary.Choice(
                "Remove orphaned recipe embeddings",
                value=self.CLEANUP_EMBEDDINGS_COMMAND,
            ),
            questionary.Choice(
                "Back to settings",
                value=self.CANCEL_COMMAND,
            ),
        ]

        return terminal.safe_select(
            "What database maintenance task do you want to run?",
            choices,
        )

    def _update_database(self):
        """
        Prompts for database update options and runs the nutrition database updater.
        """
        embedding_creation_offset = 0

        if not terminal.safe_confirm(
            "Do you really want to update the database? This may take some time."
        ):
            terminal.print_info("Database update canceled.")
            return

        skip_pipelines = not terminal.safe_confirm(
            "Do you want to run the full update pipelines? Choose 'No' to only run the embedding creation (useful if the pipelines have already been run and you just want to continue with embedding creation)."
        )

        skip_embedding_creation = not terminal.safe_confirm(
            "Do you want to create embeddings? Choose 'No' to skip embedding creation."
        )

        if not skip_embedding_creation:
            offset_answer = terminal.safe_text(
                "Type in the number of already processed records to continue an update (or leave empty to start a new update).",
                validate=non_negative_integer_and_and_configured_negative_values_or_empty(
                    [-1]
                ),
            )

            if offset_answer is None:
                terminal.print_info("Database update canceled.")
                return

            try:
                embedding_creation_offset = int(offset_answer.strip() or "0")
            except ValueError:
                terminal.print_info("The offset must be a non-negative integer.")
                return

        with suppress_console_logging(), Progress() as progress:
            result = self.__updater.update(
                progress_callback=progress.update,
                embedding_creation_offset=embedding_creation_offset,
                skip_pipelines=skip_pipelines,
                skip_embedding_creation=skip_embedding_creation,
            )

        if result["cancelled"]:
            terminal.print_info(
                "Embedding creation canceled before the final quantization step. "
                f"Continue next time with start offset {result['next_offset']}."
            )

            return

        if result.get("quantized"):
            terminal.print(
                "Database update completed successfully, including final embedding quantization! 🎉"
            )

            return

        terminal.print("Database update completed successfully! 🎉")

    def _compact_database(self):
        """
        Confirms and executes explicit SQLite compaction.
        """
        maintenance = DatabaseMaintenance(database_engine.engine)

        try:
            before = maintenance.statistics()

            terminal.print_info(
                f"Database size: {before['database_bytes']:,} bytes. "
                f"Fully free pages: {before['free_bytes']:,} bytes. "
                "Compaction can also repack partially filled pages. "
                "Back up the database and close other applications first; "
                "compaction requires exclusive access "
                "and may need up to twice the database size in additional disk space."
            )

            if not terminal.safe_confirm(
                "Compact the database now? This may take a long time.", default=False
            ):
                terminal.print_info("Database compaction canceled.")
                return

            with terminal.console.status("Compacting database..."):
                retriever_manager.close()
                maintenance.compact()

            after = maintenance.statistics()

            terminal.print_info(
                f"Database compaction completed. Size: "
                f"{before['database_bytes']:,} -> {after['database_bytes']:,} bytes."
            )
        except (SQLAlchemyError, OSError, RuntimeError) as error:
            log.exception("Database compaction failed.")
            terminal.print_info(f"Database compaction failed: {error}")

    def _create_recipe_embeddings(self):
        """
        Creates embeddings for stored recipes and displays indexing progress.
        """
        indexer = RecipeEmbeddingIndexer(configuration, database_engine)

        with Progress(bar_width=40, show_elapsed=False) as progress:
            result = indexer.create_embeddings(progress.update)

        terminal.print_info(
            f"Created embeddings for {result['created']} recipe(s); "
            f"skipped {result['skipped']} already indexed recipe(s)."
        )

    def _cleanup_recipe_embeddings(self):
        """
        Removes orphaned recipe embeddings and reports the result.
        """
        try:
            result = RecipeEmbeddingCleanup(configuration, database_engine).cleanup()
        except Exception as error:
            log.exception("Recipe embedding cleanup failed.")
            terminal.print_info(f"Recipe embedding cleanup failed: {error}")
            return

        terminal.print_info(
            f"Removed {result['removed']} orphaned recipe embedding(s); "
            f"preserved {result['unrecognized']} unrecognized recipe document(s)."
        )

