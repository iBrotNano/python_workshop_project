import pytest

from rich.progress import BarColumn, TimeElapsedColumn
from common.terminal.progress import Progress
from common.terminal.progress_update import ProgressUpdate


def test_progress_starts_new_line_for_each_phase(monkeypatch):
    renders = []

    monkeypatch.setattr(
        "common.terminal.progress.RichProgress",
        lambda *columns, **kwargs: _recording_rich_progress(renders, columns, kwargs),
    )

    progress = Progress()
    progress.update(ProgressUpdate("import", "Importing", 1, 10))
    progress.update(ProgressUpdate("import", "Importing records", 4, 10))
    progress.update(ProgressUpdate("embeddings", "Embedding records", 2, 20))

    assert len(renders) == 2

    assert renders[0]["tasks"] == [
        ("Importing", 10, 1),
    ]

    assert renders[0]["updates"] == [
        (1, "Importing records", 10, 4),
    ]

    assert renders[0]["exits"] == [(None, None, None)]

    assert renders[1]["tasks"] == [
        ("Embedding records", 20, 2),
    ]

    assert renders[0]["kwargs"]["transient"] is False
    assert renders[1]["kwargs"]["transient"] is False


def test_progress_can_use_fixed_width_without_elapsed_time(monkeypatch):
    renders = []

    monkeypatch.setattr(
        "common.terminal.progress.RichProgress",
        lambda *columns, **kwargs: _recording_rich_progress(renders, columns, kwargs),
    )

    progress = Progress(bar_width=40, show_elapsed=False)
    progress.update(ProgressUpdate("index", "Indexing recipes", 1, 10))

    bar_column = next(
        column for column in renders[0]["columns"] if isinstance(column, BarColumn)
    )

    assert bar_column.bar_width == 40

    assert not any(
        isinstance(column, TimeElapsedColumn) for column in renders[0]["columns"]
    )


def test_progress_closes_transient_line_when_context_raises(monkeypatch):
    renders = []

    monkeypatch.setattr(
        "common.terminal.progress.RichProgress",
        lambda *columns, **kwargs: _recording_rich_progress(renders, columns, kwargs),
    )

    with pytest.raises(RuntimeError, match="failed"):
        with Progress(transient=True) as progress:
            progress.update(ProgressUpdate("import", "Importing", 1, 10))
            raise RuntimeError("failed")

    assert renders[0]["kwargs"]["transient"] is True
    assert renders[0]["exits"] == [(None, None, None)]

    progress.close()
    assert renders[0]["exits"] == [(None, None, None)]


def _recording_rich_progress(renders, columns, kwargs):
    render = {
        "columns": columns,
        "kwargs": kwargs,
        "tasks": [],
        "updates": [],
        "exits": [],
    }
    renders.append(render)

    class RecordingRichProgress:
        def __enter__(self):
            return self

        def __exit__(self, exception_type, exception, traceback):
            render["exits"].append((exception_type, exception, traceback))

        def add_task(self, description, total, completed):
            render["tasks"].append((description, total, completed))
            return 1

        def update(self, task_id, description, total, completed):
            render["updates"].append((task_id, description, total, completed))

    return RecordingRichProgress()
