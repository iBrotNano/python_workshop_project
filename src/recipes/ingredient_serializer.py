import logging

from dataclasses import asdict, fields
from typing import Any
from nutrition.nutrition import Nutrition

log = logging.getLogger(__name__)


def deserialize(ingredients: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Restores nutrition objects from persisted recipe ingredients.

    :param ingredients: JSON-compatible ingredient records.
    :type ingredients: list[dict[str, Any]]
    :return: Ingredient records containing nutrition objects.
    :rtype: list[dict[str, Any]]
    :raises TypeError: If an ingredient or its food is not a dictionary.
    :raises KeyError: If a required ingredient field is missing.
    :raises ValueError: If a stored nutrition field has an invalid shape.
    """
    result = []
    field_names = {item.name for item in fields(Nutrition)}

    for ingredient in ingredients:
        if not isinstance(ingredient, dict) or not isinstance(ingredient["food"], dict):
            raise TypeError("Stored ingredients and their food must be dictionaries.")

        food = ingredient["food"]
        data = {key: value for key, value in food.items() if key in field_names}
        legacy = "name" not in food

        if legacy:
            data["name"] = food.get("product")
            data["energy_100g_kj"] = food.get("energy-kj_100g")

            if isinstance(data.get("id"), str):
                data.setdefault("code", data.pop("id"))

        brands = data.get("brands")

        if isinstance(brands, str):
            data["brands"] = [
                brand.strip() for brand in brands.split(",") if brand.strip()
            ]
        elif brands is None:
            data["brands"] = []
        elif not isinstance(brands, list) or not all(
            isinstance(brand, str) for brand in brands
        ):
            raise ValueError(
                "Stored food brands must be a string or a list of strings."
            )

        for key, value in data.items():
            if key.endswith("_100g") or key == "energy_100g_kj":
                if value is None or value == "N/A" or value == "":
                    data[key] = None
                else:
                    try:
                        data[key] = float(value)
                    except (TypeError, ValueError):
                        log.warning(
                            "Invalid stored nutrient '%s' for '%s': %r",
                            key,
                            data.get("name"),
                            value,
                        )
                        data[key] = None

        restored = {**ingredient, "food": Nutrition(**data)}

        if (legacy or food.keys() - field_names) and "_legacy_food" not in restored:
            restored["_legacy_food"] = food

        result.append(restored)

    return result


def serialize(ingredients: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Serializes recipe ingredients for JSON storage.

    :param ingredients: Ingredient records containing nutrition objects.
    :type ingredients: list[dict[str, Any]]
    :return: JSON-compatible ingredient records.
    :rtype: list[dict[str, Any]]
    :raises TypeError: If a food is not a nutrition object.
    :raises KeyError: If a required ingredient field is missing.
    """
    result = []

    for ingredient in ingredients:
        food = ingredient["food"]

        if not isinstance(food, Nutrition):
            raise TypeError("Recipe ingredient food must be a Nutrition object.")

        result.append({**ingredient, "food": asdict(food)})

    return result
