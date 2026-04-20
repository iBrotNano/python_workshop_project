from collections.abc import Callable
from common.terminal.progress_update import ProgressUpdate


ProgressCallback = Callable[[ProgressUpdate], None]


def emit_progress(
    progress_callback: ProgressCallback | None,
    phase: str,
    description: str,
    completed: int,
    total: int | None,
):
    """
    Emits a progress update if a callback was provided.

    :param progress_callback: Optional callback receiving neutral progress updates.
    :type progress_callback: ProgressCallback | None
    :param phase: Stable identifier of the current phase.
    :type phase: str
    :param description: Human-readable description of the current phase.
    :type description: str
    :param completed: Processed bytes for the current phase.
    :type completed: int
    :param total: Total bytes for the current phase if known.
    :type total: int | None
    """
    if progress_callback is None:
        return

    progress_callback(
        ProgressUpdate(
            phase=phase,
            description=description,
            completed=completed,
            total=total,
        )
    )
