import time


class Person:
    GENDERS = ("Male", "Female")

    ACTIVITY_LEVELS = {
        1: ("Sedentary (little or no exercise)", 1.2),
        2: ("Lightly active (light exercise/sports 1-3 days/week)", 1.375),
        3: ("Moderately active (moderate exercise/sports 3-5 days/week)", 1.55),
        4: ("Very active (hard exercise/sports 6-7 days a week)", 1.725),
        5: ("Super active (very hard exercise & physical job or 2x training)", 1.9),
    }

    def __init__(self):
        self.name = ""
        self.gender = ""
        self.weight = 0.0
        self.height = 0.0
        self.birth_year = 0
        self.activity_level = ""

    def calculate_calories_needed(self):
        """
        Calculates the calories needed per day based on the person's attributes.

        It uses the Mifflin–St Jeor Formela to calculate the Basal Metabolic Rate (BMR)
        and then multiplies it by an activity factor based on the person's activity level.

        :param self: This instance of the Person class.
        """
        return (
            10 * self.weight + 6.25 * self.height - 5 * self._calculate_age() + 5
            if self.gender == "Male"
            else -161
        ) * self.activity_levels[self.activity_level][1]

    def _calculate_age(self):
        """
        Calculates the age of the person based on their birthday.

        :param self: This instance of the Person class.

        :return: The age of the person.
        :rtype: int
        """
        current_year = int(time.strftime("%Y"))
        return current_year - self.birth_year
