---
marp: true
title: "Python Workshop"
paginate: true
theme: uncover
class: invert
---

# Prepare

- Delete `data` folder.
- Delete `export` folder.

---

# Start and stop the app

```powershell
z python_workshop_project
conda activate python_workshop_env
python .\src\main.py
```

Stopping through the menu or `CTRL+C` in the terminal.
Stopping is implemented everywhere in the app.

---

# Search for nutritional information

1. Search for "Müsli"
2. Paging through results
3. Select an item
4. Open web page
5. Inspect nutritional values

---

# Add recipes

1. View recipes with with no saved recipes
2. Add a new recipe
3. Inspect the nutrition of ingredients and the sum of the recipe
4. Inspect the view of the complete recipe
5. Save the recipe

---

# Export recipe

1. View the saved recipe
2. Export to Markdown

---

# Delete recipe

1. Delete the saved recipe
2. Show that it is deleted

---

# Create test recipes

I can generate test recipes with `tools/create_test_recipes.py` if needed.

```python
python tools/create_test_recipes.py
```

Inspect the `data/recipes.yaml` file afterwards.

---

# Future features

1. Add persons to the app and calculate needed calories
2. Generate meal plans based on persons and recipes
3. Generate shopping lists based on meal plans
4. Optimize the meal plans based on nutritional needs

---

# main.py

1. Explain configuration
3. Show main loop
2. Explain logging and error handling in main loop
3. Exiting the app through KeyboardInterrupt or menu option

---

# Explain architecture

1. One folder per feature
2. CommandLineHandler class for CLI interaction
3. Repository class for data access
4. Model classes for data structures

---

# questionary library

Used for command line input.

Examples: main_menu/menu.py for selection

---

# Nutritional information feature

1. Initialization in `main.py` --> `nutrition_cli.CommandLineHandler().show()`
2. User input in `_get_nutrition_search_term()`
3. Data access in `_execute_search()` with an instance of the repository.

---

# Search result

- Search with api wrapper.
- Reading only needed data from response and returning a flat dictionary.

---

# Paging through results

Pagesize is fix 7 to make it possible to use digits as shortcuts.

Navigation through the result by calling `_execute_search()` recursively with updated page number.

---

# rich library

Used for pretty printing tables and formatted text.

See `nutrition/command_line_handler.py` --> `_print_nutrition_info()`

---

# Using features from other features

Recipe feature uses nutritional information feature to search for ingredients in `command_line_handler.py` --> `_add_recipe()`.

```python
food_search = nutrition_cli.CommandLineHandler()

while True:
    food = food_search.show()
    ...
```

---

# Save to YAML files

- The repository of recipes inherits from `YamlFileRepository`.
- It encapsulates the storage path in constructor and offers methods to load and save data in superclass.
- Holds data in memory in superclass.
- Implements specific logic in subclass.
- Saves to YAML files in `data/`.
- YAML because it is human readable, easy to edit and small.