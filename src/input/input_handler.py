import logging
import questionary

log = logging.getLogger(__name__)


class InputHandler:
    EXIT_COMMAND = "EXIT"
    SEARCH_NUTRITION_COMMAND = "SEARCH_NUTRITION"

    def handle_input(self):
        """
        Handles all user input.

        :param self: The reference to the current instance of the InputHandler class.
        :return: The command entered by the user.
        """

        input_value = self._get_main_menu_input()

        return self.handle_exit(input_value)

    def _get_main_menu_input(self):
        """
        Displays the main menu and gets user input.

        :return: The command selected by the user.
        """

        choices = [
            questionary.Choice(
                "Search for nutritional information",
                value=self.SEARCH_NUTRITION_COMMAND,
            ),
            questionary.Choice(
                "Exit the application",
                value=self.EXIT_COMMAND,
            ),
        ]

        return questionary.select(
            "What do you want to do?", choices=choices, use_shortcuts=True
        ).ask()

    def handle_exit(self, input_value):
        """
        Checks if the given input value is the exit command.

        :param self: The reference to the current instance of the InputHandler class.
        :param input_value: The input value to check.
        """

        # None is returned by questionary when the user cancels the prompt (e.g., presses Ctrl+C).
        if input_value is None or input_value.upper().strip() == self.EXIT_COMMAND:

            exit_app = questionary.confirm(
                "Are you sure you want to exit?", default=False
            ).ask()

            if exit_app:
                return self.EXIT_COMMAND
