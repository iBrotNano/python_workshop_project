from dataclasses import dataclass
from datetime import date
from persons.activity_level import ActivityLevel
from persons.gender import Gender


@dataclass
class Person:
    """
    Data class representing a person with attributes relevant for calorie calculation.

    :param id: The unique identifier of the person (optional, default is 0).
    :type id: int
    :param name: The name of the person.
    :type name: str
    :param gender: The biological gender of the person.
    :type gender: Gender
    :param weight: The weight of the person in kilograms.
    :type weight: float
    :param height: The height of the person in centimeters.
    :type height: float
    :param birth_year: The birth year of the person.
    :type birth_year: int
    :param activity_level: The activity level of the person.
    :type activity_level: ActivityLevel | None
    """

    id: int = 0
    name: str = ""
    gender: Gender = Gender.MALE
    weight: float = 0.0
    height: float = 0.0
    birth_year: int = 0
    activity_level: ActivityLevel | None = None

    def __post_init__(self):
        """
        Normalizes persisted values to runtime types.

        :param self: The Person instance being initialized.
        """
        if isinstance(self.gender, str):
            try:
                self.gender = Gender(self.gender)
            except ValueError:
                self.gender = Gender.MALE

    def calories_needed(self) -> float:
        """
        Calculates the calories needed per day based on the person's attributes.

        It uses the Mifflin-St Jeor Formula to calculate the Basal Metabolic Rate (BMR)
        and then multiplies it by an activity factor based on the person's activity level.

        :param self: The Person instance for which to calculate the calories needed.
        """
        bmr_without_gender_factor = (
            10 * self.weight + 6.25 * self.height - 5 * self.age()
        )

        if self.activity_level is None:
            raise ValueError("Activity level is required to calculate calories needed.")

        return (
            bmr_without_gender_factor + (5 if self.gender == Gender.MALE else -161)
        ) * self.activity_level.multiplier

    def age(self) -> int:
        """
        Calculates the age of the person based on their birthday.

        :param self: The Person instance for which to calculate the age.
        :return: The age of the person.
        :rtype: int
        """
        current_year = date.today().year
        return current_year - self.birth_year
