import sys
from pathlib import Path

# 'src' zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from recipes.recipe_type import RecipeType
from recipes.repository import Repository
from recipes.recipe import Recipe
from persistence.database_engine_factory import database_engine

database_engine.initialize_schema()

RECIPE_TYPES = [
    RecipeType.BREAKFAST,
    RecipeType.LUNCH,
    RecipeType.DINNER,
    RecipeType.SNACK,
]

repo = Repository(next(database_engine.get_db()))

for i in range(1, 100):
    recipe_type = RECIPE_TYPES[(i - 1) % len(RECIPE_TYPES)]
    name = f"{recipe_type.value.capitalize()} Recipe {i}"

    recipe = Recipe(
        name=name,
        ingredients=[
            {
                "amount": 80,
                "food": {
                    "id": "20353889",
                    "url": "https://de.openfoodfacts.org/produkt/20353889/traube-nuss-m%C3%BCsli-68-vollkorn-crownfield",
                    "product": "Traube-Nuss M\u00fcsli 68% Vollkorn",
                    "brands": "Crownfield,Lidl",
                    "quantity": "1000g",
                    "energy-kcal_100g": 375,
                    "energy-kj_100g": 1573,
                    "carbohydrates_100g": 53.6,
                    "proteins_100g": 10.8,
                    "fat_100g": 10.6,
                    "sugars_100g": 11.2,
                    "salt_100g": 0.07,
                    "added-sugars": 0.285,
                    "added-sugars_100g": 0.285,
                    "added-sugars_modifier": "~",
                    "added-sugars_unit": "g",
                    "added-sugars_value": 0.285,
                    "carbohydrates": 53.6,
                    "carbohydrates_unit": "g",
                    "carbohydrates_value": 53.6,
                    "energy": 1573,
                    "energy-kcal": 375,
                    "energy-kcal_unit": "kcal",
                    "energy-kcal_value": 375,
                    "energy-kj": 1573,
                    "energy-kj_unit": "kJ",
                    "energy-kj_value": 1573,
                    "energy_100g": 1573,
                    "energy_unit": "kJ",
                    "energy_value": 1573,
                    "fat": 10.6,
                    "fat_unit": "g",
                    "fat_value": 10.6,
                    "fiber": 10.8,
                    "fiber_100g": 10.8,
                    "fiber_unit": "g",
                    "fiber_value": 10.8,
                    "fruits-vegetables-legumes-estimate-from-ingredients_100g": 18,
                    "fruits-vegetables-nuts-estimate-from-ingredients_100g": 25,
                    "nova-group": 3,
                    "nova-group_100g": 3,
                    "nova-group_serving": 3,
                    "nova-group_unit": "",
                    "nova-group_value": 3,
                    "proteins": 10.8,
                    "proteins_unit": "g",
                    "proteins_value": 10.8,
                    "salt": 0.07,
                    "salt_unit": "g",
                    "salt_value": 0.07,
                    "saturated-fat": 2.7,
                    "saturated-fat_100g": 2.7,
                    "saturated-fat_unit": "g",
                    "saturated-fat_value": 2.7,
                    "sodium": 0.028,
                    "sodium_100g": 0.028,
                    "sodium_unit": "g",
                    "sodium_value": 0.028,
                    "sugars": 11.2,
                    "sugars_unit": "g",
                    "sugars_value": 11.2,
                },
            }
        ],
        instructions="Mischen und essen.",
        nutrition={
            "calories": 494.0,
            "energy": 2081.4,
            "fat": 13.0,
            "carbohydrates": 56.480000000000004,
            "protein": 33.96,
            "sugar": 22.56,
            "salt": 0.506,
        },
        type=recipe_type,
    )

    repo.try_add(recipe)
print(f"Created test recipe recipes.yaml")
