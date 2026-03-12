from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.theme import Theme


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


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
terminal = Terminal()
