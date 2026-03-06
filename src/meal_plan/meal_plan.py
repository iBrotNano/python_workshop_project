import random

from meal_plan.meal import Meal
from recipes.repository import Repository
import recipes.recipe_types as rt


class MealPlan:
    def __init__(self):
        """
        Initializes the MealPlan.

        :param self: This instance of the MealPlan class.
        """
        self.meals: list[list[Meal]] = []  # Matrix: 7 days, 5 meals per day

        self.recipes_repository = Repository()

    def generate(self):
        """
        Generates a new meal plan by assigning random recipes to each meal.

        :param self: This instance of the MealPlan class.
        """
        for day in range(7):
            self.meals.append([])  # Add a new day column
            for meal_time in range(5):
                self.meals[day].append(Meal())

                recipe = self._get_recipe(rt.RECIPE_TYPE_MAPPINGS[meal_time])

                if recipe:
                    self.meals[day][meal_time].set_recipe(recipe)

    def _get_recipe(self, recipe_type: str):
        """
        Gets a random recipe that has been assigned to any meal in the plan only if there are not enough recipes to fill the plan for a meal time.

        If no recipe is available for a meal time, None is returned.

        :param self: This instance of the MealPlan class.
        :param recipe_type: The type of recipe to filter by.
        :type recipe_type: str
        :return: A random recipe that has not been assigned, or None if all recipes are assigned.
        :rtype: Recipe | None
        """
        already_assigned_recipes = {
            meal.recipe.name
            for day in self.meals
            for meal in day
            if meal.recipe is not None
        }

        return self.recipes_repository.get_random_recipe_by(
            recipe_type, assigned=already_assigned_recipes
        )

    def is_meal_plan_generated(self) -> bool:
        """
        Checks if the meal plan has been generated.

        :param self: This instance of the MealPlan class.
        :return: True if the meal plan is generated, False otherwise.
        """
        return any(any(meal.recipe is not None for meal in day) for day in self.meals)
