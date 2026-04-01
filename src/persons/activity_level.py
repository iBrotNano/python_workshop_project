from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from persons.person import Person


@dataclass
class ActivityLevel:
    """Data model representing an activity level for a person."""

    id: int = 0
    name: str = ""
    multiplier: float = 0.0
    persons: list["Person"] = field(default_factory=list)
