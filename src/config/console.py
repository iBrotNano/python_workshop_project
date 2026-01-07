from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel

# Defines a theme for the console output.
custom_theme = Theme({"info": "cyan", "info_border": "dim cyan"})

# Use this singleton as the console throughout the application.
console = Console(theme=custom_theme)


def configure():
    """
    Configure the global console object with a custom theme.

    This function applies a predefined custom theme to the global console instance,
    updating its visual appearance and styling according to the custom theme configuration.
    """
    global console
    console.use_theme(custom_theme)


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
