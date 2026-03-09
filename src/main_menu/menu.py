import logging
import questionary

log = logging.getLogger(__name__)


class Menu:
    EXIT_COMMAND = "EXIT"
    SEARCH_NUTRITION_COMMAND = "SEARCH_NUTRITION"
    MANAGE_RECIPES_COMMAND = "MANAGE_RECIPES"
    MANAGE_MEAL_PLAN_COMMAND = "MANAGE_MEAL_PLAN"
    MANAGE_PERSONS_COMMAND = "MANAGE_PERSONS"

    def show(self):
        """
        Shows the main menu and handles it's selection.

        :return: The user's selection.
        """

        selection = self._get_main_menu_selection()

        # None is returned by questionary when the user cancels the prompt (e.g., presses Ctrl+C).
        if selection is None or selection == self.EXIT_COMMAND:
            return self._confirm_exit()

        return selection

    def _get_main_menu_selection(self):
        """
        Displays the main menu and gets the user's selection.

        :return: The command selected by the user.
        """

        choices = [
            questionary.Choice(
                "Search for nutritional information",
                value=self.SEARCH_NUTRITION_COMMAND,
            ),
            questionary.Choice("Manage recipes", value=self.MANAGE_RECIPES_COMMAND),
            questionary.Choice("Manage meal plan", value=self.MANAGE_MEAL_PLAN_COMMAND),
            questionary.Choice("Manage persons", value=self.MANAGE_PERSONS_COMMAND),
            questionary.Choice(
                "Exit the application",
                value=self.EXIT_COMMAND,
            ),
        ]

        return questionary.select(
            "What do you want to do?", choices=choices, use_shortcuts=True
        ).ask()

    def _confirm_exit(self):
        """
        Confirms that the user wants to exit the application.

        :return: The exit command if the user confirms, otherwise None.
        """

        exit_app = questionary.confirm(
            "Are you sure you want to exit?", default=False
        ).ask()

        if exit_app:
            return self.EXIT_COMMAND
