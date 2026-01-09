recipes = ""

for i in range(1, 100):
    recipes += f"""Test{i}:
  ingredients:
  - amount: 100
    product:
      brands: ja!
      carbohydrates: 9.5
      carbohydrates_100g: 9.5
      carbohydrates_serving: 14.2
      carbohydrates_unit: g
      carbohydrates_value: 9.5
      energy: 330
      energy-kcal: 78
      energy-kcal_100g: 78
      energy-kcal_serving: 117
      energy-kcal_unit: kcal
      energy-kcal_value: 78
      energy-kcal_value_computed: 75
      energy-kj: 330
      energy-kj_100g: 330
      energy-kj_serving: 495
      energy-kj_unit: kJ
      energy-kj_value: 330
      energy-kj_value_computed: 318.5
      energy_100g: 330
      energy_serving: 495
      energy_unit: kJ
      energy_value: 330
      fat: 0.2
      fat_100g: 0.2
      fat_serving: 0.3
      fat_unit: g
      fat_value: 0.2
      fruits-vegetables-legumes-estimate-from-ingredients_100g: 4.35
      fruits-vegetables-legumes-estimate-from-ingredients_serving: 4.35
      fruits-vegetables-nuts-estimate-from-ingredients_100g: 4.35
      fruits-vegetables-nuts-estimate-from-ingredients_serving: 4.35
      id: '4337256182393'
      nova-group: 4
      nova-group_100g: 4
      nova-group_serving: 4
      nutrition-score-fr: -1
      nutrition-score-fr_100g: -1
      product: Skyr
      proteins: 8.8
      proteins_100g: 8.8
      proteins_serving: 13.2
      proteins_unit: g
      proteins_value: 8.8
      quantity: 1pcs
      salt: 0.16
      salt_100g: 0.16
      salt_serving: 0.24
      salt_unit: g
      salt_value: 0.16
      saturated-fat: 0.1
      saturated-fat_100g: 0.1
      saturated-fat_serving: 0.15
      saturated-fat_unit: g
      saturated-fat_value: 0.1
      sodium: 0.064
      sodium_100g: 0.064
      sodium_serving: 0.096
      sodium_unit: g
      sodium_value: 0.064
      sugars: 8.7
      sugars_100g: 8.7
      sugars_serving: 13
      sugars_unit: g
      sugars_value: 8.7
      url: https://de.openfoodfacts.org/produkt/4337256182393/skyr-ja
  instructions: Test
  name: Test{i}\n"""

with open(f"data/recipes_testdata.yaml", "w", encoding="utf-8") as f:
    f.write("".join(recipes))

print(f"Created test recipe recipes_testdata.yaml")
