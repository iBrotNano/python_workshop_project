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

    def __init__(
        self,
        name: str = "",
        gender: str = "",
        weight: float = 0.0,
        height: float = 0.0,
        birth_year: int = 0,
        activity_level: int = 0,
    ):
        self.name = name
        self.gender = gender
        self.weight = weight
        self.height = height
        self.birth_year = birth_year
        self.activity_level = activity_level

    @staticmethod
    def calculate_calories_needed(person: "Person") -> float:
        """
        Calculates the calories needed per day based on the person's attributes.

        It uses the Mifflin-St Jeor Formula to calculate the Basal Metabolic Rate (BMR)
        and then multiplies it by an activity factor based on the person's activity level.

        :param person: The Person instance for which to calculate the calories needed.
        """
        return (
            10 * person.weight
            + 6.25 * person.height
            - 5 * person.calculate_age(person)
            + 5
            if person.gender == "Male"
            else -161
        ) * Person.ACTIVITY_LEVELS[person.activity_level][1]

    @staticmethod
    def calculate_age(person: "Person") -> int:
        """
        Calculates the age of the person based on their birthday.

        :param person: The Person instance for which to calculate the age.
        :return: The age of the person.
        :rtype: int
        """
        current_year = int(time.strftime("%Y"))
        return current_year - person.birth_year
