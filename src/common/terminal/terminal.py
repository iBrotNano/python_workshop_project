import questionary
import logging

from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.theme import Theme
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.output.win32 import NoConsoleScreenBufferError
from typing import Any, Callable, Dict, Sequence, Union
from common.terminal.input_validators import always_true

log = logging.getLogger(__name__)


class Terminal:
    """
    A class that encapsulates the terminal output functionality using the Rich library.
    """

    def __init__(self):
        """
        Initializes the Terminal with a custom theme and console instance.

        The terminal is meant to be used for all console output in the application, providing a consistent look and feel. It should be used as a singleton.

        :param self: This instance of the Terminal class.
        """

        # Defines a theme for the console output.
        self._custom_theme: Theme = Theme({"info": "cyan", "info_border": "dim cyan"})

        self._console: Console = Console(theme=self._custom_theme)

    @property
    def console(self) -> Console:
        """
        Provides access to the console instance for printing output.

        :return: The console instance for printing output.
        """

        return self._console

    def print(self, *args, **kwargs):
        """
        Print a message to the console.

        :param self: This instance of the Terminal class.
        :param args: Positional arguments to pass to the console's print method.
        :param kwargs: Keyword arguments to pass to the console's print method.
        """

        self._console.print(*args, **kwargs)

    def print_rule_separated(self, message: str):
        """
        Print a standard message followed by a separator rule.

        :param self: This instance of the Terminal class.
        :param message: The message to print before the separator.
        """

        self._console.print(message)
        self._console.rule()

    def print_info(self, message: str, title: str = "INFO"):
        """
        Print an informational message framed by themed rules.

        :param self: This instance of the Terminal class.
        :param message: The informational message to display.
        :param title: The title for the information panel with the default 'INFO'.
        """

        self._console.print(
            Panel(
                f"[info]:information_source: {title}[/info]\n  {message}",
                border_style="info_border",
            )
        )

    def print_dict_as_table(
        self,
        values: dict[str, str],
        column1_title: str,
        column2_title: str,
    ):
        """
        Prints a table with two columns.

        :param values: A dictionary mapping names (str) to their corresponding values (str).
        :param column1_title: The title for the first column.
        :param column2_title: The title for the second column.
        """

        table = Table()
        table.add_column(column1_title, style="cyan", no_wrap=True)
        table.add_column(column2_title, style="magenta")

        for key, value in values.items():
            table.add_row(key, str(value))

        self._console.print(table)

    def text(
        self, message: str, default: str = "", validate: Callable = always_true
    ) -> questionary.Question:
        """
        Asks a free-text question using Questionary with a TTY-preferred backend.

        :param self: This instance of the Terminal class.
        :param message: The message shown to the user.
        :type message: str
        :param default: The default value if the user provides no input.
        :type default: str
        :param validate: A callable to validate the input.
        :type validate: Callable
        :return: A Questionary text question instance.
        :rtype: questionary.Question

        """
        return questionary.text(
            message,
            input=create_input(always_prefer_tty=True),
            output=create_output(always_prefer_tty=True),
            default=default,
            validate=validate,
        )

    def safe_text(
        self, message: str, default: str = "", validate: Callable = always_true
    ) -> Any:
        """
        Asks a free-text question using Questionary with a TTY-preferred backend.

        :param self: This instance of the Terminal class.
        :param message: The message shown to the user.
        :type message: str
        :param default: The default value if the user provides no input.
        :type default: str
        :return: The entered text or None if the prompt was cancelled.
        :rtype: Any
        """
        for _ in range(2):
            try:
                return self.text(message, default, validate).ask()
            except NoConsoleScreenBufferError:
                log.warning(
                    "Questionary could not access the Windows console buffer. Retrying."
                )

        log.error("The interactive prompt could not be reopened in this terminal.")

        raise RuntimeError(
            "Failed to display interactive prompt after multiple attempts."
        )

    def select(
        self,
        message: str,
        choices: Sequence[Union[str, questionary.Choice, Dict[str, Any]]],
    ) -> questionary.Question:
        """
        Asks a select question using Questionary with a TTY-preferred backend.

        :param self: This instance of the Terminal class.
        :param message: The message shown to the user.
        :type message: str
        :param choices: The selectable choices.
        :type choices: Sequence[Union[str, questionary.Choice, Dict[str, Any]]]
        :return: A Questionary select question instance.
        :rtype: questionary.Question
        """
        return questionary.select(
            message,
            choices=choices,
            use_shortcuts=True,
            input=create_input(always_prefer_tty=True),
            output=create_output(always_prefer_tty=True),
        )

    def safe_select(
        self,
        message: str,
        choices: Sequence[Union[str, questionary.Choice, Dict[str, Any]]],
    ) -> Any:
        """
        Displays a Questionary select prompt with a TTY-preferred backend.

        :param message: The menu question shown to the user.
        :param choices: The selectable choices.
        :type choices: Sequence[Union[str, questionary.Choice, Dict[str, Any]]]
        :return: The selected value or None if the prompt was cancelled.
        :rtype: Any
        """
        for _ in range(2):
            try:
                return self.select(message, choices).ask()
            except NoConsoleScreenBufferError:
                log.warning(
                    "Questionary could not access the Windows console buffer. Retrying."
                )

        raise RuntimeError(
            "Failed to display interactive select prompt after multiple attempts."
        )

    def confirm(self, message: str, default: bool = False) -> questionary.Question:
        """
        Asks a confirmation question using Questionary with a TTY-preferred backend.

        :param self: This instance of the Terminal class.
        :param message: The message shown to the user.
        :type message: str
        :param default: The default value if the user provides no input.
        :type default: bool
        :return: A Questionary confirmation question instance.
        :rtype: questionary.Question

        """
        return questionary.confirm(
            message,
            default=default,
            input=create_input(always_prefer_tty=True),
            output=create_output(always_prefer_tty=True),
        )

    def safe_confirm(self, message: str, default: bool = False) -> Any:
        """
        Displays a Questionary confirmation prompt with a TTY-preferred backend.

        :param message: The confirmation question shown to the user.
        :param default: The default confirmation value.
        :return: True, False, or None if the prompt could not be shown.
        :rtype: Any
        """
        for _ in range(2):
            try:
                return self.confirm(message, default).ask()
            except NoConsoleScreenBufferError:
                log.warning(
                    "Questionary could not access the Windows console buffer. Retrying."
                )

        raise RuntimeError(
            "Failed to display interactive confirmation prompt after multiple attempts."
        )


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
terminal = Terminal()
