from dataclasses import dataclass

from rich.progress import (
    Progress,
    TaskID,
)


@dataclass
class ProgressState:
    """Stores the active Rich task state for sequential persistence progress."""

    progress: Progress | None = None
    task_id: TaskID | None = None
    phase: str | None = None
