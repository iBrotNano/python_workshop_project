from meal_plan.meal_plan import MealPlan


class Repository:
    def __init__(self):
        """
        Initializes the Repository.

        :param self: This instance of the Repository class.
        """
        self.meal_plan = MealPlan()

    def get(self):
        """
        Gets the current meal plan.

        :param self: This instance of the Repository class.
        :return: The current meal plan.
        """
        return self.meal_plan
