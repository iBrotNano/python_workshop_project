from meal_plan.meal_plan import MealPlan


class Repository:
    """Repository class that holds the meal plan."""

    def __init__(self, meal_plan: MealPlan):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        :param meal_plan: An instance of the MealPlan class.
        :type meal_plan: MealPlan
        """
        self._meal_plan = meal_plan

    @property
    def meal_plan(self) -> MealPlan:
        """
        Returns the meal plan.

        :param self: This instance of the Repository class.
        :return: The meal plan.
        :rtype: MealPlan
        """
        return self._meal_plan
