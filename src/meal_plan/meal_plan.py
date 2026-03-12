from meal_plan.meal import Meal


class MealPlan:
    """Represents a meal plan, which is a matrix of meals for each day of the week and meal time. 7 days, 5 meals per day"""

    def __init__(self):
        """
        Initializes the MealPlan with an empty plan.

        :param self: This instance of the MealPlan class.
        """
        self._plan: list[list[Meal | None]] = [
            [None for _ in range(5)] for _ in range(7)
        ]

    @property
    def plan(self) -> list[list[Meal | None]]:
        """
        Returns the meal plan.

        :param self: This instance of the MealPlan class.
        :return: The meal plan, which is a list of lists containing Meal objects or None.
        :rtype: list[list[Meal | None]]
        """
        return self._plan

    def clear(self):
        """
        Clears the meal plan by resetting all meals to None.

        :param self: This instance of the MealPlan class.
        """
        self._plan = [[None for _ in range(5)] for _ in range(7)]

    def set_meal(self, day: int, meal_time: int, meal: Meal):
        """
        Sets a meal for a specific day and meal time in the meal plan.

        :param self: This instance of the MealPlan class.
        :param day: The index of the day (0-6) for which to set the meal.
        :param meal_time: The index of the meal time (0-4) for which to set the meal.
        :param meal: The Meal object to set in the meal plan.
        """
        self._plan[day][meal_time] = meal

    def get_assigned_recipes(self) -> set[str]:
        """
        Retrieves the names of all recipes that have been assigned to meals in the meal plan.

        :param self: This instance of the MealPlan class.
        :return: A set of recipe names that are currently assigned in the meal plan.
        :rtype: set[str]
        """
        return {
            meal.recipe.name
            for day in self._plan
            for meal in day
            if meal is not None and meal.recipe is not None
        }

    def is_meal_plan_filled(self) -> bool:
        """
        Checks if the meal plan has been filled.

        :param self: This instance of the MealPlan class.
        :return: True if the meal plan is filled, False otherwise.
        """
        return all(
            all(meal is not None and meal.recipe is not None for meal in day)
            for day in self._plan
        )
