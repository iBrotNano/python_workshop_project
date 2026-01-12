import logging
import questionary
from meal_plan.repository import Repository
from meal_plan.meal_plan import MealPlan
from common.console import print_info
from config.console import console

log = logging.getLogger(__name__)


class CommandLineHandler:
    CANCEL_COMMAND = "CANCEL"
    GENERATE_MEAL_PLAN_COMMAND = "GENERATE_MEAL_PLAN"

    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        :param repository: The meal plan repository.
        :type repository: Repository
        """
        self.repository = Repository()

    def show(self):
        """
        Shows the meal plan management menu.

        :param self: This instance of the CommandLineHandler class.
        """
        while True:
            if not self.repository.get().is_meal_plan_generated():
                print_info("No meal plan is present.")

            command = self._get_recipe_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return  # User chose to cancel; return to main menu.

            if command == self.GENERATE_MEAL_PLAN_COMMAND:
                self._generate_meal_plan()

    def _get_recipe_menu_selection(self):
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
        self.repository.get().generate()
        print_info("A new meal plan has been generated and saved.")

        # TODO: Show the generated meal plan in a nice table.
        for day_index, day in enumerate(self.repository.get().meals):
            console.print(f"[bold underline]Day {day_index + 1}[/bold underline]")
            for meal_index, meal in enumerate(day):
                console.print(f"[bold]Meal {meal_index + 1}:[/bold] {meal.recipe.name}")
