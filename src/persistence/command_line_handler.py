import logging

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from common.terminal import terminal
from config.configuration import configuration
from persistence.nutrition_db_updater import NutritionDbUpdater
from common.progress_state import ProgressState
from common.progress_update import ProgressUpdate
from common.console_logging_suppressor import suppress_console_logging
from persistence.database_engine_factory import database_engine
from common.input_validators import non_negative_integer_or_empty

log = logging.getLogger(__name__)


class CommandLineHandler:
    """Handles the command line flow for persistence-related actions."""

    def __init__(self):
        """
        Initializes the persistence command line handler.

        :param self: The CommandLineHandler instance being initialized."""
        self.__updater = NutritionDbUpdater(configuration, database_engine)

    def show(self):
        """
        Prompts the user and renders progress for the database update.

        :param self: The CommandLineHandler instance handling the command line flow.
        """
        if not terminal.safe_confirm(
            "Do you really want to update the database? This may take some time."
        ):
            terminal.print_info("Database update canceled.")
            return

        offset_answer = terminal.safe_text(
            "Type in the number of already processed records to continue an update (or leave empty to start a new update).",
            validate=non_negative_integer_or_empty,
        )

        if offset_answer is None:
            terminal.print_info("Database update canceled.")
            return

        try:
            embedding_creation_offset = int(offset_answer.strip() or "0")
        except ValueError:
            terminal.print_info("The offset must be a non-negative integer.")
            return

        progress_state = ProgressState()

        with suppress_console_logging():
            try:
                result = self.__updater.update(
                    progress_callback=lambda update: self.__sync_progress_state(
                        progress_state,
                        update,
                    ),
                    embedding_creation_offset=embedding_creation_offset,
                )
            finally:
                self.__close_progress(progress_state)

        if result["cancelled"]:
            terminal.print_info(
                f"Embedding creation canceled. Continue next time with start offset {result['next_offset']}."
            )
            return

        terminal.print("Database update completed successfully! 🎉")

    def __sync_progress_state(
        self,
        progress_state: ProgressState,
        update: ProgressUpdate,
    ):
        """
        Updates the mutable progress state for the single visible Rich task.

        :param progress_state: Mutable state containing task identifier and phase.
        :type progress_state: ProgressState
        :param update: The latest progress update from the updater.
        :type update: ProgressUpdate
        """
        if progress_state.phase != update.phase:
            self.__close_progress(progress_state)
            progress_state.progress = self.__create_progress(transient=False)
            progress_state.progress.__enter__()
            progress_state.task_id = progress_state.progress.add_task(
                update.description,
                total=update.total,
                completed=update.completed,
            )
            progress_state.phase = update.phase
            return

        if progress_state.progress is None or progress_state.task_id is None:
            raise RuntimeError("Progress state is not initialized.")

        self.__handle_progress_update(
            progress_state.progress,
            progress_state.task_id,
            update,
        )

    def __handle_progress_update(
        self,
        progress: Progress,
        task_id: TaskID,
        update: ProgressUpdate,
    ):
        """
        Synchronizes updater progress events with Rich progress tasks.

        :param progress: The Rich progress instance used for rendering.
        :type progress: Progress
        :param task_id: The active Rich task identifier.
        :type task_id: TaskID
        :param update: The latest progress update from the updater.
        :type update: ProgressUpdate
        """
        progress.update(
            task_id,
            description=update.description,
            total=update.total,
            completed=update.completed,
        )

    def __close_progress(self, progress_state: ProgressState):
        """
        Closes the active Rich progress instance and keeps its final line visible.

        :param progress_state: Mutable state containing the active progress instance.
        :type progress_state: ProgressState
        """
        if progress_state.progress is None:
            return

        progress_state.progress.__exit__(None, None, None)
        progress_state.progress = None
        progress_state.task_id = None

    def __create_progress(self, transient: bool) -> Progress:
        """
        Creates a Rich progress view for persistence operations.

        :param transient: Whether the progress display should be removed on exit.
        :type transient: bool
        :return: Configured Rich progress instance.
        :rtype: Progress
        """
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, finished_style="green"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=terminal.console,
            transient=transient,
        )
