from meal_plan.meal import Meal
from meal_plan.meal_plan import MealPlan
from recipes.repository import Repository
from recipes.recipe import Recipe
from recipes.recipe_type import RecipeType


class MealPlanner:
    """
    Generates a meal plan by assigning random recipes to each meal time for each day of the week. It uses a MealPlan to hold the assigned meals and a Repository to fetch and store recipes.
    """

    MEAL_SLOTS = {
        0: RecipeType.BREAKFAST,
        1: RecipeType.SNACK,
        2: RecipeType.LUNCH,
        3: RecipeType.SNACK,
        4: RecipeType.DINNER,
    }

    def __init__(self, meal_plan: MealPlan, recipe_repository: Repository):
        """
        Initializes the MealPlanner.

        :param self: This instance of the MealPlanner class.
        :param meal_plan: An instance of the MealPlan class to hold the assigned meals.
        :param recipe_repository: An instance of the Repository class to fetch and store recipes.
        """
        self._meal_plan = meal_plan
        self._recipes_repository = recipe_repository

    def generate(self):
        """
        Generates a new meal plan by assigning random recipes to each meal.

        :param self: This instance of the MealPlanner class.
        """
        self._meal_plan.clear()

        for day in range(7):
            for meal_time in range(5):
                recipe = self._get_recipe(self.MEAL_SLOTS[meal_time])

                if recipe:
                    self._meal_plan.set_meal(day, meal_time, Meal(recipe))

    def _get_recipe(self, recipe_type: str) -> Recipe | None:
        """
        Gets a random recipe that has been assigned to any meal in the plan only if there are not enough recipes to fill the plan for a meal time.

        If no recipe is available for a meal time, None is returned.

        :param self: This instance of the MealPlanner class.
        :param recipe_type: The type of recipe to filter by.
        :type recipe_type: str
        :return: A random recipe that has not been assigned, or None if all recipes are assigned.
        :rtype: Recipe | None
        """

        return self._recipes_repository.get_random_recipe_by(
            recipe_type, assigned=self._meal_plan.get_assigned_recipes()
        )
