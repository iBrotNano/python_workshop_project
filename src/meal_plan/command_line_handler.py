import logging
import questionary

from meal_plan.repository import Repository
from recipes.repository import Repository as RecipesRepository
from common.terminal import terminal
from rich.table import Table
from meal_plan.meal_planner import MealPlanner
from meal_plan.meal_plan import MealPlan

log = logging.getLogger(__name__)


class CommandLineHandler:
    """Handles the command line interface for meal plan management."""

    CANCEL_COMMAND = "CANCEL"
    GENERATE_MEAL_PLAN_COMMAND = "GENERATE_MEAL_PLAN"

    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        :param repository: The meal plan repository.
        :type repository: Repository
        """

        self._meal_plan = MealPlan()
        self._repository = Repository(self._meal_plan)
        self._recipe_repository = RecipesRepository()
        self._meal_planner = MealPlanner(self._meal_plan, self._recipe_repository)

    def show(self):
        """
        Shows the meal plan management menu.

        :param self: This instance of the CommandLineHandler class.
        """
        while True:
            if not self._repository.meal_plan.is_meal_plan_filled():
                terminal.print_info("No meal plan is present.")

            command = self._get_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return  # User chose to cancel; return to main menu.

            if command == self.GENERATE_MEAL_PLAN_COMMAND:
                self._generate_meal_plan()

    def _get_menu_selection(self):
        """
        Displays the menu and gets the user's selection.

        :param self: This instance of the CommandLineHandler class.

        :return: The command selected by the user.
        """

        choices = [
            questionary.Choice(
                "Generate a new meal plan",
                value=self.GENERATE_MEAL_PLAN_COMMAND,
            ),
            questionary.Choice(
                "Back to main menu",
                value=self.CANCEL_COMMAND,
            ),
        ]

        return questionary.select(
            "What do you want to do?", choices=choices, use_shortcuts=True
        ).ask()

    def _generate_meal_plan(self):
        """
        Generates a new meal plan and saves it to the repository.

        :param self: This instance of the CommandLineHandler class.
        """

        def _display_meal_plan():
            """
            Displays the current meal plan in a table format.
            """
            table = Table(show_lines=True)
            table.add_column("Meal", style="bold magenta")
            table.add_column("Monday", style="cyan")
            table.add_column("Tuesday", style="white")
            table.add_column("Wednesday", style="cyan")
            table.add_column("Thursday", style="white")
            table.add_column("Friday", style="cyan")
            table.add_column("Saturday", style="white")
            table.add_column("Sunday", style="cyan")

            for meal_index, meal_name in MealPlanner.MEAL_SLOTS.items():
                row_data = [meal_name.capitalize()]

                for day in self._meal_plan.plan:
                    meal = day[meal_index]

                    row_data.append(
                        meal.recipe.name
                        if meal is not None and meal.recipe is not None
                        else "N/A"
                    )

                table.add_row(*row_data)

            terminal.print(table)

        self._meal_planner.generate()
        terminal.print_info("A new meal plan has been generated and saved.")
        _display_meal_plan()
