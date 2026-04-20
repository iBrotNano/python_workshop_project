import logging
import sys
import main_menu.menu as menu
import nutrition.command_line_handler as nutrition_cli
import recipes.command_line_handler as recipe_cli
import meal_plan.command_line_handler as meal_plan_cli
import persons.command_line_handler as persons_cli
import persistence.command_line_handler as persistence_cli
from prompt_toolkit.output.win32 import NoConsoleScreenBufferError

from common.terminal.terminal import terminal
from config.configurator import configurator
from config.configuration import configuration
from persistence.database_engine_factory import database_engine


log = logging.getLogger(__name__)

# Encapsulates the whole application logic and displays any errors encountered.
try:
    configurator.configure(
        configuration
    )  # First step configures the app (e.g., logging, console).

    database_engine.initialize_schema()
    main_menu = menu.Menu()

    while True:
        try:
            command = main_menu.show()

            if command == main_menu.SEARCH_NUTRITION_COMMAND:
                nutrition_cli.CommandLineHandler().show()

            if command == main_menu.MANAGE_RECIPES_COMMAND:
                recipe_cli.CommandLineHandler().show()

            if command == main_menu.MANAGE_MEAL_PLAN_COMMAND:
                meal_plan_cli.CommandLineHandler().show()

            if command == main_menu.MANAGE_PERSONS_COMMAND:
                persons_cli.CommandLineHandler().show()

            if command == main_menu.UPDATE_DATABASE_COMMAND:
                persistence_cli.CommandLineHandler().show()

            if command == main_menu.EXIT_COMMAND:
                terminal.print("Goodbye! 👋")
                sys.exit(0)
        except NoConsoleScreenBufferError as e:
            terminal.print(
                "No interactive Windows console was detected. Start the app from cmd.exe, "
                "PowerShell, or the VS Code integrated terminal."
            )
            sys.exit(1)
        except Exception as e:
            log.exception(f"An error of type {type(e)} occurred. Message: {e}")

# Catch any unexpected errors at the top level during app initialization.
except Exception as e:
    log.critical(f"An error of type {type(e)} occurred. Message: {e}", exc_info=True)
    sys.exit(1)  # Exit with error code 1 to indicate failure.
