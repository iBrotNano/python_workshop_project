import logging
import sys
import main_menu.menu as menu
import nutrition.command_line_handler as nutrition_cli
import recipes.command_line_handler as recipe_cli
import meal_plan.command_line_handler as meal_plan_cli
import persons.command_line_handler as persons_cli

from common.terminal import terminal
from config.configurator import configurator


log = logging.getLogger(__name__)

# Encapsulates the whole application logic and displays any errors encountered.
try:
    configurator.configure()  # First step configures the app (e.g., logging, console).
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

            if command == main_menu.EXIT_COMMAND:
                terminal.print("Goodbye! 👋")
                sys.exit(0)

        except Exception as e:
            log.exception(f"An error of type {type(e)} occurred. Message: {e}")

# Catch any unexpected errors at the top level during app initialization.
except Exception as e:
    log.critical(f"An error of type {type(e)} occurred. Message: {e}", exc_info=True)
    sys.exit(1)  # Exit with error code 1 to indicate failure.
