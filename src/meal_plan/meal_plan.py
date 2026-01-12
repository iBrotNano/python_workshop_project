from meal_plan.meal import Meal
from recipes.repository import Repository
import recipes.recipe_types as rt


class MealPlan:
    def __init__(self):
        """
        Initializes the MealPlan.

        :param self: This instance of the MealPlan class.
        """
        self.meals = [
            [None for _ in range(5)] for _ in range(7)
        ]  # 7 days, 5 meals per day

        self.recipes_repository = Repository()

        self.recipe_type_mapping = {
            0: rt.BREAKFAST,
            1: rt.SNACK,
            2: rt.LUNCH,
            3: rt.SNACK,
            4: rt.DINNER,
        }

    def generate(self):
        """
        Generates a new meal plan by assigning random recipes to each meal.

        :param self: This instance of the MealPlan class.
        """
        for day in range(7):
            for meal_time in range(5):
                self.meals[day][meal_time] = Meal()

                self.meals[day][meal_time].set_recipe(
                    self.recipes_repository.get_random_recipe(
                        self.recipe_type_mapping[meal_time]
                    )
                )

    def is_meal_plan_generated(self) -> bool:
        """
        Checks if the meal plan has been generated.

        :param self: This instance of the MealPlan class.
        :return: True if the meal plan is generated, False otherwise.
        """
        return any(any(meal is not None for meal in day) for day in self.meals)
