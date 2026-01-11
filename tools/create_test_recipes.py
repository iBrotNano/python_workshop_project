import sys
from pathlib import Path

# 'src' zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from recipes import recipe_types as rt

recipes = ""

for i in range(1, 100):
    recipes += f"""Test Rezept {i}:
  ingredients:
  - amount: 80
    product:
      brands: Crownfield (Lidl)
      carbohydrates: 66.7
      carbohydrates_100g: 66.7
      carbohydrates_serving: 13.3
      carbohydrates_unit: g
      carbohydrates_value: 66.7
      carbon-footprint-from-known-ingredients_100g: 55.15
      carbon-footprint-from-known-ingredients_product: 414
      carbon-footprint-from-known-ingredients_serving: 11
      energy: 1611
      energy-kcal: 382
      energy-kcal_100g: 382
      energy-kcal_serving: 76.4
      energy-kcal_unit: kcal
      energy-kcal_value: 382
      energy-kcal_value_computed: 382.1
      energy-kj: 1611
      energy-kj_100g: 1611
      energy-kj_serving: 322
      energy-kj_unit: kJ
      energy-kj_value: 1611
      energy-kj_value_computed: 1610.7
      energy_100g: 1611
      energy_serving: 322
      energy_unit: kJ
      energy_value: 1611
      fat: 7.1
      fat_100g: 7.1
      fat_serving: 1.42
      fat_unit: g
      fat_value: 7.1
      fiber: 8.7
      fiber_100g: 8.7
      fiber_serving: 1.74
      fiber_unit: g
      fiber_value: 8.7
      fruits-vegetables-legumes-estimate-from-ingredients_100g: 63.25
      fruits-vegetables-legumes-estimate-from-ingredients_serving: 63.25
      fruits-vegetables-nuts-estimate: 20
      fruits-vegetables-nuts-estimate-from-ingredients_100g: 63.25
      fruits-vegetables-nuts-estimate-from-ingredients_serving: 63.25
      fruits-vegetables-nuts-estimate_100g: 20
      fruits-vegetables-nuts-estimate_label: '0'
      fruits-vegetables-nuts-estimate_serving: 20
      fruits-vegetables-nuts-estimate_unit: g
      fruits-vegetables-nuts-estimate_value: 20
      id: '20202866'
      nova-group: 4
      nova-group_100g: 4
      nova-group_serving: 4
      nutrition-score-fr: 6
      nutrition-score-fr_100g: 6
      product: premium müsli
      proteins: 8.5
      proteins_100g: 8.5
      proteins_serving: 1.7
      proteins_unit: g
      proteins_value: 8.5
      quantity: 750 g
      salt: 0.07
      salt_100g: 0.07
      salt_serving: 0.014
      salt_unit: g
      salt_value: 0.07
      saturated-fat: 2.3
      saturated-fat_100g: 2.3
      saturated-fat_serving: 0.46
      saturated-fat_unit: g
      saturated-fat_value: 2.3
      sodium: 0.028
      sodium_100g: 0.028
      sodium_serving: 0.0056
      sodium_unit: g
      sodium_value: 0.028
      sugars: 25.1
      sugars_100g: 25.1
      sugars_serving: 5.02
      sugars_unit: g
      sugars_value: 25.1
      url: https://de.openfoodfacts.org/produkt/20202866/premium-m%C3%BCsli-mit-fr%C3%BCchten-und-kernen-crownfield-lidl
  - amount: 150
    product:
      brands: Berchtesgadener Land, Bergbauern
      calcium: 0.124
      calcium_100g: 0.124
      calcium_label: '0'
      calcium_unit: g
      calcium_value: 0.124
      carbohydrates: 5
      carbohydrates_100g: 5
      carbohydrates_unit: g
      carbohydrates_value: 5
      energy: 275
      energy-kcal: 66
      energy-kcal_100g: 66
      energy-kcal_unit: kcal
      energy-kcal_value: 66
      energy-kcal_value_computed: 66
      energy-kj: 275
      energy-kj_100g: 275
      energy-kj_unit: kJ
      energy-kj_value: 275
      energy-kj_value_computed: 276
      energy_100g: 275
      energy_unit: kJ
      energy_value: 275
      fat: 3.6
      fat_100g: 3.6
      fat_unit: g
      fat_value: 3.6
      fruits-vegetables-legumes-estimate-from-ingredients_100g: 0
      fruits-vegetables-legumes-estimate-from-ingredients_serving: 0
      fruits-vegetables-nuts-estimate-from-ingredients_100g: 0
      fruits-vegetables-nuts-estimate-from-ingredients_serving: 0
      id: '4101530002475'
      nova-group: 1
      nova-group_100g: 1
      nova-group_serving: 1
      nutrition-score-fr: 4
      nutrition-score-fr_100g: 4
      product: H-Milch
      proteins: 3.4
      proteins_100g: 3.4
      proteins_unit: g
      proteins_value: 3.4
      quantity: 1l
      salt: 0.11
      salt_100g: 0.11
      salt_unit: g
      salt_value: 0.11
      saturated-fat: 2.4
      saturated-fat_100g: 2.4
      saturated-fat_unit: g
      saturated-fat_value: 2.4
      sodium: 0.044
      sodium_100g: 0.044
      sodium_unit: g
      sodium_value: 0.044
      sugars: 5
      sugars_100g: 5
      sugars_unit: g
      sugars_value: 5
      url: https://de.openfoodfacts.org/produkt/4101530002475/h-milch-berchtesgadener-land
  instructions: Mischen und essen.
  name: Test Rezept {i}
  nutrition:
    calories: 404.6
    carbohydrates: 60.86000000000001
    energy: 1701.3000000000002
    fat: 11.08
    protein: 11.9
    salt: 0.22100000000000003
    sugar: 27.580000000000002
  type: {rt.RECIPE_TYPES[i % 4]}\n"""

with open(f"data/recipes_testdata.yaml", "w", encoding="utf-8") as f:
    f.write("".join(recipes))

print(f"Created test recipe recipes_testdata.yaml")
