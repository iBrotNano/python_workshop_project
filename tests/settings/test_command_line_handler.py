from contextlib import nullcontext
import runpy
from types import SimpleNamespace

import pytest

from main_menu.menu import Menu
from recipes.command_line_handler import CommandLineHandler as RecipeCommandLineHandler
from settings.command_line_handler import CommandLineHandler


def test_settings_database_menu_is_reachable_from_main_menu(monkeypatch):
    main_choices = []
    settings_choices = []

    monkeypatch.setattr(
        "main_menu.menu.terminal.safe_select",
        lambda message, choices: main_choices.extend(choices),
    )

    Menu()._get_main_menu_selection()

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_select",
        lambda message, choices: settings_choices.extend(choices),
    )

    CommandLineHandler()._get_settings_menu_selection()

    assert CommandLineHandler.MANAGE_DATABASE_COMMAND in [
        choice.value for choice in settings_choices
    ]

    assert Menu.OPEN_SETTINGS_COMMAND in [choice.value for choice in main_choices]


def test_database_menu_contains_all_maintenance_tasks(monkeypatch):
    choices = []

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_select",
        lambda message, menu_choices: choices.extend(menu_choices),
    )

    CommandLineHandler()._get_database_menu_selection()

    assert [choice.value for choice in choices] == [
        CommandLineHandler.UPDATE_DATABASE_COMMAND,
        CommandLineHandler.COMPACT_DATABASE_COMMAND,
        CommandLineHandler.CREATE_EMBEDDINGS_COMMAND,
        CommandLineHandler.CLEANUP_EMBEDDINGS_COMMAND,
        CommandLineHandler.CANCEL_COMMAND,
    ]


def test_settings_menu_opens_database_menu(monkeypatch):
    selections = iter(
        [
            CommandLineHandler.MANAGE_DATABASE_COMMAND,
            CommandLineHandler.CANCEL_COMMAND,
        ]
    )

    opened = []
    handler = CommandLineHandler()

    monkeypatch.setattr(
        handler,
        "_get_settings_menu_selection",
        lambda: next(selections),
    )

    monkeypatch.setattr(
        handler,
        "_show_database_menu",
        lambda: opened.append(True),
    )

    handler.show()

    assert opened == [True]


@pytest.mark.parametrize(
    ("command", "expected_action"),
    [
        (CommandLineHandler.UPDATE_DATABASE_COMMAND, "update"),
        (CommandLineHandler.COMPACT_DATABASE_COMMAND, "compact"),
        (CommandLineHandler.CREATE_EMBEDDINGS_COMMAND, "create_embeddings"),
        (CommandLineHandler.CLEANUP_EMBEDDINGS_COMMAND, "cleanup_embeddings"),
    ],
)
def test_database_menu_executes_selected_task(monkeypatch, command, expected_action):
    actions = []
    selections = iter([command, CommandLineHandler.CANCEL_COMMAND])
    handler = CommandLineHandler()

    monkeypatch.setattr(
        handler,
        "_get_database_menu_selection",
        lambda: next(selections),
    )

    monkeypatch.setattr(
        handler,
        "_update_database",
        lambda: actions.append("update"),
    )

    monkeypatch.setattr(
        handler,
        "_compact_database",
        lambda: actions.append("compact"),
    )

    monkeypatch.setattr(
        handler,
        "_create_recipe_embeddings",
        lambda: actions.append("create_embeddings"),
    )
    monkeypatch.setattr(
        handler,
        "_cleanup_recipe_embeddings",
        lambda: actions.append("cleanup_embeddings"),
    )

    handler._show_database_menu()

    assert actions == [expected_action]


def test_database_update_calls_updater_directly(monkeypatch):
    calls = []
    updater = SimpleNamespace(
        update=lambda **kwargs: (
            calls.append(kwargs)
            or {"cancelled": False, "next_offset": 0, "quantized": False}
        )
    )

    confirmations = iter([True, True, False])

    monkeypatch.setattr(
        "settings.command_line_handler.NutritionDbUpdater",
        lambda *args: updater,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: next(confirmations),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print",
        lambda *args, **kwargs: None,
    )

    CommandLineHandler()._update_database()

    assert len(calls) == 1
    assert calls[0]["skip_pipelines"] is False
    assert calls[0]["skip_embedding_creation"] is True


def test_database_update_cancellation_does_not_run_updater(monkeypatch):
    updates = []
    messages = []
    updater = SimpleNamespace(update=lambda **kwargs: updates.append(kwargs))

    monkeypatch.setattr(
        "settings.command_line_handler.NutritionDbUpdater",
        lambda *args: updater,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: False,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print_info",
        messages.append,
    )

    CommandLineHandler()._update_database()

    assert updates == []
    assert messages == ["Database update canceled."]


def test_database_update_offset_cancellation_does_not_run_updater(monkeypatch):
    updates = []
    messages = []
    updater = SimpleNamespace(update=lambda **kwargs: updates.append(kwargs))
    confirmations = iter([True, True, True])

    monkeypatch.setattr(
        "settings.command_line_handler.NutritionDbUpdater",
        lambda *args: updater,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: next(confirmations),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_text",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print_info",
        messages.append,
    )

    CommandLineHandler()._update_database()

    assert updates == []
    assert messages == ["Database update canceled."]


def test_database_update_reports_cancelled_offset(monkeypatch):
    updates = []
    messages = []
    updater = SimpleNamespace(
        update=lambda **kwargs: updates.append(kwargs)
        or {"cancelled": True, "next_offset": 42, "quantized": False}
    )

    confirmations = iter([True, True, True])

    monkeypatch.setattr(
        "settings.command_line_handler.NutritionDbUpdater",
        lambda *args: updater,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: next(confirmations),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_text",
        lambda *args, **kwargs: "7",
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print_info",
        messages.append,
    )

    CommandLineHandler()._update_database()

    assert updates[0]["embedding_creation_offset"] == 7
    assert messages == [
        "Embedding creation canceled before the final quantization step. "
        "Continue next time with start offset 42."
    ]


def test_database_update_reports_quantized_completion(monkeypatch):
    messages = []
    updater = SimpleNamespace(
        update=lambda **kwargs: {
            "cancelled": False,
            "next_offset": 0,
            "quantized": True,
        }
    )

    confirmations = iter([True, True, False])

    monkeypatch.setattr(
        "settings.command_line_handler.NutritionDbUpdater",
        lambda *args: updater,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: next(confirmations),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print",
        messages.append,
    )

    CommandLineHandler()._update_database()

    assert messages == [
        "Database update completed successfully, including final embedding quantization! 🎉"
    ]


def test_database_compaction_calls_maintenance_directly(monkeypatch):
    actions = []
    statistics = iter(
        [
            {"database_bytes": 100, "free_bytes": 20},
            {"database_bytes": 80, "free_bytes": 0},
        ]
    )
    maintenance = SimpleNamespace(
        statistics=lambda: next(statistics),
        compact=lambda: actions.append("compact"),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.DatabaseMaintenance",
        lambda *args: maintenance,
    )
    monkeypatch.setattr(
        "settings.command_line_handler.retriever_manager",
        SimpleNamespace(close=lambda: actions.append("close")),
    )
    monkeypatch.setattr(
        "settings.command_line_handler.terminal.safe_confirm",
        lambda *args, **kwargs: True,
    )
    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print_info",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "settings.command_line_handler.terminal._console",
        SimpleNamespace(status=lambda *args, **kwargs: _null_context()),
    )

    CommandLineHandler()._compact_database()

    assert actions == ["close", "compact"]


def test_recipe_maintenance_calls_domain_services_directly(monkeypatch):
    actions = []
    progress_options = []

    indexer = SimpleNamespace(
        create_embeddings=lambda callback: actions.append("create")
        or {"created": 1, "skipped": 0}
    )

    cleanup = SimpleNamespace(
        cleanup=lambda: actions.append("cleanup") or {"removed": 1, "unrecognized": 0}
    )

    monkeypatch.setattr(
        "settings.command_line_handler.RecipeEmbeddingIndexer",
        lambda *args: indexer,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.RecipeEmbeddingCleanup",
        lambda *args: cleanup,
    )

    monkeypatch.setattr(
        "settings.command_line_handler.Progress",
        lambda *args, **kwargs: (progress_options.append(kwargs) or _fake_progress()),
    )

    monkeypatch.setattr(
        "settings.command_line_handler.terminal.print_info",
        lambda *args, **kwargs: None,
    )

    handler = CommandLineHandler()
    handler._create_recipe_embeddings()
    handler._cleanup_recipe_embeddings()

    assert actions == ["create", "cleanup"]
    assert progress_options == [{"bar_width": 40, "show_elapsed": False}]


def test_old_menus_no_longer_contain_database_tasks(monkeypatch):
    main_choices = []
    recipe_choices = []

    monkeypatch.setattr(
        "main_menu.menu.terminal.safe_select",
        lambda message, choices: main_choices.extend(choices),
    )
    monkeypatch.setattr(
        "recipes.command_line_handler.questionary.select",
        lambda message, choices, use_shortcuts: SimpleNamespace(
            ask=lambda: recipe_choices.extend(choices)
        ),
    )

    Menu()._get_main_menu_selection()
    RecipeCommandLineHandler()._get_recipe_menu_selection()

    assert [choice.value for choice in main_choices] == [
        Menu.OPEN_ASSISTANT_COMMAND,
        Menu.SEARCH_NUTRITION_COMMAND,
        Menu.MANAGE_RECIPES_COMMAND,
        Menu.MANAGE_MEAL_PLAN_COMMAND,
        Menu.MANAGE_PERSONS_COMMAND,
        Menu.OPEN_SETTINGS_COMMAND,
        Menu.EXIT_COMMAND,
    ]
    assert [choice.value for choice in recipe_choices] == [
        RecipeCommandLineHandler.VIEW_RECIPE_COMMAND,
        RecipeCommandLineHandler.ADD_RECIPE_COMMAND,
        RecipeCommandLineHandler.DELETE_RECIPE_COMMAND,
        RecipeCommandLineHandler.CANCEL_COMMAND,
    ]


def test_main_dispatches_open_settings_command(monkeypatch):
    actions = []
    selections = iter(
        [
            Menu.OPEN_SETTINGS_COMMAND,
            Menu.EXIT_COMMAND,
        ]
    )

    monkeypatch.setattr(
        "config.configurator.configurator.configure",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "persistence.database_engine_factory.database_engine.initialize_schema",
        lambda: None,
    )
    monkeypatch.setattr(
        "main_menu.menu.Menu.show",
        lambda self: next(selections),
    )
    monkeypatch.setattr(
        "settings.command_line_handler.CommandLineHandler.show",
        lambda self: actions.append("settings"),
    )
    monkeypatch.setattr(
        "persistence.retriever_manager.retriever_manager.close",
        lambda: None,
    )
    monkeypatch.setattr(
        "common.terminal.terminal.terminal.print",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(SystemExit) as error:
        runpy.run_path("src\\main.py", run_name="main_test")

    assert error.value.code == 0
    assert actions == ["settings"]


def _null_context():
    return nullcontext()


def _fake_progress():
    class FakeProgress:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def add_task(self, *args, **kwargs):
            return 1

        def update(self, *args, **kwargs):
            pass

    return FakeProgress()
