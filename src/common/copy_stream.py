from typing import BinaryIO, Callable
from common.terminal.progress_callback import ProgressCallback, emit_progress


class CopyStream:
    """
    Utility for copying byte streams while emitting progress updates.
    """

    @staticmethod
    def copy(
        source,
        target: BinaryIO,
        phase: str,
        description: str,
        total: int | None,
        progress_callback: ProgressCallback | None = None,
        position_reader: Callable[[], int] | None = None,
        chunk_size: int = 1024 * 1024,
    ):
        """
        Copies a stream in chunks while emitting progress updates.

        :param source: Source stream that supports reading bytes.
        :param target: Target stream that supports writing bytes.
        :type target: BinaryIO
        :param phase: Stable identifier of the current phase.
        :type phase: str
        :param description: Human-readable description of the current phase.
        :type description: str
        :param total: Total bytes for the current phase if known.
        :type total: int | None
        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :param position_reader: Optional reader for obtaining processed byte position.
        :type position_reader: Callable[[], int] | None
        """
        completed = 0

        while chunk := source.read(chunk_size):
            target.write(chunk)

            if position_reader is None:
                completed += len(chunk)
            else:
                current_position = position_reader()
                completed = max(current_position, completed)

            emit_progress(
                progress_callback,
                phase=phase,
                description=description,
                completed=completed,
                total=total,
            )

        if total is not None:
            emit_progress(
                progress_callback,
                phase=phase,
                description=description,
                completed=total,
                total=total,
            )
