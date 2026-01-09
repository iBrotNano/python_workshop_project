from config.console import console
from rich.panel import Panel
from rich.table import Table


def print_rule_separated(message: str):
    """Print a standard message followed by a separator rule.

    Args:
        message: The message to display.
    """
    console.print(message)
    console.rule()


def print_info(message: str, title: str = "INFO"):
    """Print an informational message framed by themed rules.

    Args:
        message: The informational message to display.
        title: The title for the information panel with the default 'INFO'.
    """
    console.print(
        Panel(
            f"[info]:information_source: {title}[/info]\n  {message}",
            border_style="info_border",
        )
    )


def print_dict_as_table(
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

    console.print(table)
