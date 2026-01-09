from rich.console import Console
from rich.theme import Theme

# Defines a theme for the console output.
custom_theme = Theme({"info": "cyan", "info_border": "dim cyan"})

# Use this singleton as the console throughout the application.
console = Console(theme=custom_theme)
