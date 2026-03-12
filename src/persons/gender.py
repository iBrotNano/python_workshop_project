from enum import Enum


class Gender(str, Enum):
    """Enum class representing biological gender."""

    MALE = "Male"
    FEMALE = "Female"
