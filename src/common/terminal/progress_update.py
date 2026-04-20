from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressUpdate:
    """
    Represents a progress update emitted by the nutrition database updater.

    :param phase: Stable identifier of the current update phase.
    :type phase: str
    :param description: Human-readable description of the current phase.
    :type description: str
    :param completed: Processed bytes for the current phase.
    :type completed: int
    :param total: Total bytes for the current phase if known.
    :type total: int | None
    """

    phase: str
    description: str
    completed: int
    total: int | None
