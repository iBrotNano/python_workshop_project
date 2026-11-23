from types import TracebackType
from common.terminal.progress_update import ProgressUpdate
from common.terminal.terminal import terminal

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress as RichProgress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)


class Progress:
    """
    Displays progress updates and keeps sequential phases on separate lines.
    """

    def __init__(
        self,
        transient: bool = False,
        bar_width: int | None = None,
        show_elapsed: bool = True,
    ):
        """
        Initializes the progress display.

        :param transient: Whether completed progress lines should be removed.
        :type transient: bool
        :param bar_width: Width of the progress bar, or None to use available space.
        :type bar_width: int | None
        :param show_elapsed: Whether to display elapsed time.
        :type show_elapsed: bool
        """
        self.__transient = transient
        self.__bar_width = bar_width
        self.__show_elapsed = show_elapsed
        self.__progress: RichProgress | None = None
        self.__task_id: TaskID | None = None
        self.__phase: str | None = None

    def __enter__(self) -> "Progress":
        """
        Returns the progress display for use as a context manager.

        :return: This progress display.
        :rtype: Progress
        """
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Closes the active progress display.
        """
        self.close()

    def update(self, update: ProgressUpdate) -> None:
        """
        Renders a progress update, starting a new task for each new phase.

        :param update: The progress state to display.
        :type update: ProgressUpdate
        """
        if update.phase != self.__phase:
            self.close()
            self.__progress = self.__create_progress()
            self.__progress.__enter__()

            self.__task_id = self.__progress.add_task(
                update.description,
                total=update.total,
                completed=update.completed,
            )

            self.__phase = update.phase
            return

        if self.__progress is None or self.__task_id is None:
            raise RuntimeError("Progress display is not initialized.")

        self.__progress.update(
            self.__task_id,
            description=update.description,
            total=update.total,
            completed=update.completed,
        )

    def close(self) -> None:
        """
        Closes the current progress line while retaining completed output.
        """
        if self.__progress is not None:
            self.__progress.__exit__(None, None, None)

        self.__progress = None
        self.__task_id = None
        self.__phase = None

    def __create_progress(self) -> RichProgress:
        """
        Creates the Rich progress renderer.

        :return: Configured Rich progress renderer.
        :rtype: RichProgress
        """
        columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=self.__bar_width, finished_style="green"),
            MofNCompleteColumn(),
        ]

        if self.__show_elapsed:
            columns.append(TimeElapsedColumn())

        return RichProgress(
            *columns,
            console=terminal.console,
            transient=self.__transient,
        )
