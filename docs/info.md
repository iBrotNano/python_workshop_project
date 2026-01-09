## :dart: Requirements

### :spiral_notepad: Description

#### MVP

1. Development of a simple CLI tool to query nutritional information from an API (https://publicapis.io/open-food-facts-api, https://platform.fatsecret.com/platform-api). Search for foods and display nutrition facts.
   - Search criteria are name and manufacturer.
2. Create recipes with nutrition calculation.
   - Users can enter recipes, and the tool calculates the overall nutritional values based on the ingredients.
   - Ingredients are selected via product search. Ingredient quantities in the recipe must be specified, optionally with the number of people the recipe is intended for.
   - Recipes are saved as a JSON file and can be loaded again later.
   - Quantity information is persisted per person.

#### Optional Features
3. Create a weekly meal plan from the recipes.
   - Users can assign recipes to a day of the week.
4. Generate a shopping list based on the meal plan.
   - The tool generates a shopping list with the required ingredients and quantities.
   - The number of people must be specified to scale the quantities correctly.
5. Save the shopping list to Google Keep.
   - Integration with the Google Keep API to save the shopping list directly to Google Keep.

### :question: Open Questions?
1. @Who: What must be discussed?

### :construction: Blockers

1. Something blocks my work.

### :inbox_tray: Input
Command line input from the user. Selections and search terms. With the search term, the API is queried to get the data. Depending on the selections the user makes, the main functions are called. Ingredients from recipes are typed in by the user.

### :outbox_tray: Output

- Search results from the API displayed in the console.
- Nutritional values of recipes displayed in the console.
- Shopping list displayed in the console.
- Recipes saved as JSON files.
- Shopping list saved to Google Keep.
- Error messages in case of failures.
- Help messages for user guidance.
- Confirmation messages for actions like saving files or sending data to Google Keep.
- Summary reports of nutritional values for recipes and meal plans.
- Configuration settings for API access and user preferences.
- User prompts for input and selections.

### :control_knobs: Conditions

- The app is locally executed on the user's machine. The user must have internet access to query the API and to save the shopping list to Google Keep.
- The user must have a Google account to use the Google Keep integration.
- The user must have Python installed on their machine to run the CLI tool.
- The user must have an API key for the nutritional information API if required.

### :warning: Side effects

Are there any?

## :heavy_check_mark: Acceptance tests
- [ ] I will test that the app can exits gracefully.
- [ ] All errors are handled gracefully with appropriate messages in the console.
- [ ] All errors are written into a log file with timestamps for debugging purposes.
- [ ] I will test searching for foods by name and manufacturer and verify that the correct nutritional information is displayed.
- [ ] I will test creating recipes by entering ingredients and quantities, and verify that the overall nutritional values are calculated correctly.
- [ ] I will test saving and loading recipes as JSON files to ensure data integrity.
- [ ] I will test creating a weekly meal plan by assigning recipes to days of the week.
- [ ] I will test generating a shopping list based on the meal plan and verify that the required ingredients and quantities are correct.
- [ ] I will test saving the shopping list to Google Keep and verify that it appears correctly in the user's Google Keep account.
- [ ] I will test that the app provides clear status messages, error messages, help messages, and confirmation messages to guide the user through the operations.
- [ ] I will test that the app handles invalid inputs gracefully and provides appropriate feedback to the user.
- [ ] I will test that the app can handle network errors when querying the API or saving to Google Keep, and provides appropriate error messages.
- [ ] I will test that the app can be configured with different API keys and user preferences.

## :triangular_ruler: Design

### Summary

The app will be a CLI tool developed in Python. It will use requests to interact with the nutritional information API and Google Keep API. The app will have functions for searching foods, creating recipes, generating meal plans, and saving shopping lists. I will use an OOP approach to structure the code, with classes for handling API interactions, recipe management, meal planning, and user input/output.

### Error handling

Error handling will be implemented to ensure that all errors are logged and displayed appropriately. Errors will be logged into files with timestamps for debugging purposes and displayed in the console for user awareness. All exceptions will be caught and handled gracefully to prevent the app from crashing.

### Input and output handling

There are some helpful libraries to handle input in CLI apps. They can handle selections and other stuff i will need. I will use [questionary](https://github.com/tmbo/questionary) to handle input from the user. Output will be displayed enriched in the console using [rich](https://github.com/Textualize/rich).

Every feature of the app will have its own input and output handling functions to keep the code organized and maintainable.

### Nutritional information API

An existing API will be queried to get nutritional information. The app will handle user input via the command line and display output in the console.

## :microscope: Dissection

| Integration test | 1                                                                        |
| ---------------- | ------------------------------------------------------------------------ |
| Action           | I will exit the app selecting "Exit the application" from the main menu. |
| Expected result  | The app should terminate gracefully without errors.                      |

| Integration test | 2                                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| Action           | I will provoke an error by not configuring something important.                                      |
| Expected result  | The errors are handled gracefully and the app does not crash. The error is displayed in the console. |

| Integration test | 3                                                                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will provoke an error by not configuring something important.                                                                     |
| Expected result  | A logfile is created with detailed error information for debugging purposes. The error details include timestamps and stack traces. |

| Integration test | 4                                                               |
| ---------------- | --------------------------------------------------------------- |
| Action           | I will exit the app via the main menu by confirming the prompt. |
| Expected result  | The app should terminate gracefully without errors.             |

| Integration test | 5                                                                 |
| ---------------- | ----------------------------------------------------------------- |
| Action           | I will navigate to the nutrition information search via the menu. |
| Expected result  | The navigation works                                              |

| Integration test | 6                                                   |
| ---------------- | --------------------------------------------------- |
| Action           | I will exit the app via CTRL+C in the main menu.    |
| Expected result  | The app should terminate gracefully without errors. |  |

| Integration test | 7                                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| Action           | I will check if the confirmation before exit is triggered and performs and prevents the exit correctly. |
| Expected result  | The confirmation before exit should be recognized.                                                      |

| Integration test | 8                                                             |
| ---------------- | ------------------------------------------------------------- |
| Action           | I will enter en empty string as a search term.                |
| Expected result  | The app returns to the main menu without performing a search. |

| Integration test | 9                                                             |
| ---------------- | ------------------------------------------------------------- |
| Action           | I will press CTRL+C in the search term question.              |
| Expected result  | The app returns to the main menu without performing a search. |

| Integration test | 10                                                            |
| ---------------- | ------------------------------------------------------------- |
| Action           | I will search for a non-existent product.                     |
| Expected result  | The app displays a message indicating no products were found. |

| Integration test | 11                                                                                                          |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| Action           | I will search for a existent product.                                                                       |
| Expected result  | The app displays all found products and i can select one. The selected product is displayed with it's data. |

| Integration test | 12                                                                                 |
| ---------------- | ---------------------------------------------------------------------------------- |
| Action           | I will search for a existent product and navigate through the pages of the result. |
| Expected result  | I can navigate through the pages of the search results. Forward and backward.      |

| Integration test | 13                                                                    |
| ---------------- | --------------------------------------------------------------------- |
| Action           | I will search for a existent product and cancel the process via menu. |
| Expected result  | The app returns to the main menu without displaying a search result.  |

| Integration test | 14                                                                        |
| ---------------- | ------------------------------------------------------------------------- |
| Action           | I will search for a existent product and cancel the process via `CTRL+C`. |
| Expected result  | The app returns to the main menu without displaying a search result.      |

| Integration test | 15                                                               |
| ---------------- | ---------------------------------------------------------------- |
| Action           | I will navigate to the feature 'Manage Recipes'.                 |
| Expected result  | I will see a selection of features related to recipe management. |

| Integration test | 16                                                                                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will add a new recipe and cancel it.                                                                                                                                          |
| Expected result  | I will be prompted to enter a name for the recipe. If i cancel it with `CTRL+C`, the process is aborted and I return to the recipe management menu. A logging message is shown. |

| Integration test | 17                                                                                                                                 |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will add a new recipe and enter an empty string as name.                                                                         |
| Expected result  | If I enter an empty string as name, the process is aborted and I return to the recipe management menu. A logging message is shown. |

| Integration test | 18                                          |
| ---------------- | ------------------------------------------- |
| Action           | I will exit `Manage recipes` with `CTRL+C`. |
| Expected result  | I navigate back to the main menu.           |

| Integration test | 19                                                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will add a new recipe with a duplicate name.                                                                                                                |
| Expected result  | A warning message is shown indicating that a recipe with the same name already exists. The user is prompted for a different name as long as they want to try. |

| Integration test | 20                                                                                                                                                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will add a new ingredient to the recipe.                                                                                                                                                                                  |
| Expected result  | The ingredient is stored with the recipe instance. After I have selected a ingredient a prompt forces me to enter an amount in grams per person. After I entered the amount the ingredient and amount are shown in a table. |

| Integration test | 21                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will cancel the addition of an ingredient by pressing `CTRL+C`.                                                         |
| Expected result  | A prompt is shown asking if I want to add another ingredient. If I choose not to, I return to the recipe management menu. |

| Integration test | 22                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will cancel the addition of an ingredient by selecting `Cancel` in the found products.                                  |
| Expected result  | A prompt is shown asking if I want to add another ingredient. If I choose not to, I return to the recipe management menu. |

| Integration test | 23                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will cancel the addition of an ingredient by pressing `CTRL+C` in the amount prompt.                                    |
| Expected result  | A prompt is shown asking if I want to add another ingredient. If I choose not to, I return to the recipe management menu. |

| Integration test | 24                                                    |
| ---------------- | ----------------------------------------------------- |
| Action           | I will enter multiline instructions to the recipe.    |
| Expected result  | The instructions are stored with the recipe instance. |

| Integration test | 25                                                  |
| ---------------- | --------------------------------------------------- |
| Action           | I will cancel entering instructions for the recipe. |
| Expected result  | I return to the recipe management menu.             |

| Integration test | 26                                                           |
| ---------------- | ------------------------------------------------------------ |
| Action           | I will enter an empty string as instructions for the recipe. |
| Expected result  | I return to the recipe management menu.                      |

| Integration test | 27                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will cancel the saving of the recipe during the save prompt.                                                                                  |
| Expected result  | A confirmation prompt is shown asking if I really want to cancel saving the recipe. If I choose not to, I return to the recipe management menu. |

| Integration test | 28                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will deny saving the recipe during the save prompt.                                                                                           |
| Expected result  | A confirmation prompt is shown asking if I really want to cancel saving the recipe. If I choose not to, I return to the recipe management menu. |

| Integration test | 29                                         |
| ---------------- | ------------------------------------------ |
| Action           | I will save 2 recipes.                     |
| Expected result  | Both recipes are stored in a file as json. |

| Integration test | 30                                                                        |
| ---------------- | ------------------------------------------------------------------------- |
| Action           | I will try to add an existing recipe after restarting the app.            |
| Expected result  | The name is already present in the repository and no new recipe is added. |

| Integration test | 31                                                                |
| ---------------- | ----------------------------------------------------------------- |
| Action           | I will open `Manage recipes` with not present `data/recipes.json` |
| Expected result  | The app works and I can add the first recipe.                     |

| Integration test | 32                                                                                                                            |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will add a recipe and check that the sums of macronutrients are correct.                                                    |
| Expected result  | The calculation is correct and matches the sum of individual ingredients during the addition and at the end in before saving. |

| Integration test | 33                                                                                           |
| ---------------- | -------------------------------------------------------------------------------------------- |
| Action           | I will delete a recipe. `tools/create_test_recipes.py` can be used to generate test recipes. |
| Expected result  | The recipe is deleted from memory and the file.                                              |

## :hammer_and_wrench: Development

### :clipboard: TODOs

- [x] Exit the app when the user types "exit" (case insensitive, ignoring leading/trailing spaces)
- [x] Handle all errors gracefully with appropriate messages in the console
- [x] Timestamp for error logging in the console
- [x] Log all errors into a log file with timestamps for debugging purposes
- [x] Use Lib for input to make app handling easier
- [x] Add menue to select between the main functions and exit
- [x] Ask for confirmation before exiting the app
- [x] Development of a simple CLI tool to query nutritional information from an API (https://publicapis.io/open-food-facts-api, https://platform.fatsecret.com/platform-api). Search for foods and display nutrition facts.
  - [x] Make the name of my app configurable
  - [x] Make the version of my app configurable
  - [x] Check the API [world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
    - [x] Inspect the returned data structure
    - [x] Remove the hint to enter 'exit'
    - [x] Implement the test code from `main.py` into the repository class
    - [x] Delete `api_call.py`
    - [x] Output the search results in a user friendly way
    - [x] ~~Can the search be made more performant? I also want only results with at least the macronutrients filled.~~
  - [x] Configuration settings for API access and user preferences.
  - [x] Search criteria are name and manufacturer.
  - [x] Configuration for the logger in `config.py`
  - [x] Extract console handling into own feature modules
  - [x] Use number from result and paging information
  - [x] Search results from the API displayed in the console as a new selection.
  - [x] Make the Items in the selection more user friendly
  - [x] Display nutrition without table style
  - [x] Handle zero results gracefully with 'Ja kyr'
  - [x] Cancel the search via menu
  - [x] Fixes missing shortcuts
  - [x] Paging for the selection if there are many results.
  - [x] Make output more user friendly with `rich`
    - [x] Initialize the console via `config/console.py`
    - [x] Show 7 items per page.
    - [x] Coloring the buttons 'Next' and 'Previous' to make them more visible.
    - [x] Show 'Next' if more results are available.
    - [x] Show 'Previous' if not on the first page.
    - [x] Show the current shown items and the total number of items.
    - [x] Show disabled 'Next' and 'Previous' buttons gray when not available.
  - [x] Nutritional values displayed in the console as a table with [Tables — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/tables.html) or [Layout — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/layout.html).
    - [x] What data should be displayed?
    - [x] Are the results normalized?
    - [x] What possible values are there for the nutrients?
    - [x] Link to the search item on openfoodfacts.org as header for result
- [x] Create recipes with nutrition calculation.
  - [x] Main menu entry for recipe management
  - [x] Cancel the recipe management via menu
  - [x] Add recipe as selection
  - [x] User can enter a name for a recipe.
  - [x] Add ingredients to the recipe via product search.
  - [x] What happens when the addition of ingredients is cancelled?
  - [x] Add multiple ingredients to the recipe.
  - [x] Specify ingredient quantities in the recipe.
    - [x] Cancellation should navigate to the recipe management menu.
  - [x] Show the added ingredients and amount as a table.
  - [x] No table if no ingredients are added yet.
  - [x] Add instructions to the recipe.
    - [x] Handle cancellation
    - [x] Handle empty instructions
  - [x] Recipes can be stored to disk.
    - [x] Names must be unique.
    - [x] Show the complete recipe before asking to persist it to disk.
    - [x] Show ingredients as links
    - [x] Confirm before cancelling the saving of the recipe.
    - [x] Configure the path where recipes are stored.
    - [x] Load recipes from disk.
  - [x] Users can enter recipes, and the tool calculates the overall nutritional values based on the ingredients.
    - [x] Show the nutrients summed up for all ingredients during adding ingredients.
    - [x] Protein and sugar is not correctly calculated.
    - [x] Add the unit to the nutrient values.
    - [x] Round to 2 decimal places.
    - [x] Capitalize the nutrient names.
    - [x] Headline for nutrition table in the markdown output.
    - [x] Disply nutrition as table in the markdown output.
  - [x] Ingredients are selected via product search. Ingredient quantities in the recipe must be specified, optionally with the number of people the recipe is intended for.
  - [x] Recipes are saved as a JSON file and can be loaded again later. (Maybe YAML?) How to input recipe instuctions?
  - [x] Quantity information is persisted per person.
  - [x] Check if i can handle recipes with markdown files. I could use [Markdown — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/markdown.html) to display them nicely in the console.
- [x] Is it possible to show the names of the ingredients as links in the nutritional search result? :x:
- [x] `recipes.yaml` could not be read because of not supported tuples. Fix it.
- [x] Extract console methods in the folder `common`
- [x] I searched for [Bio Spagetti Vollkorn – Edeka – 500](https://de.openfoodfacts.org/produkt/4311501653821/bio-spagetti-vollkorn-edeka) and it caused an error because N/A can not be converted to float. Handle it gracefully.
- [x] Delete recipes
  - [x] Add a menu entry to delete recipes.
  - [x] Search for a recipe with autocomplete
  - [x] Only the autocomplete items are valid
  - [x] Confirm before deleting a recipe.
  - [x] Delete the recipe from memory and the file.
- [x] Do I need the handling of the Cancellation of the add command? :heavy_check_mark:
- [x] View recipes
  - [x] Add a menu entry to view recipes.
  - [x] Show all existing recipes with autocomplete
  - [x] Display the selected recipe in markdown format in the console.
- [x] Export recipes as markdown files with nutritional information
  - [x] The nutritional information calculated for recipes must be stored with the recipe.
  - [x] Modify the tool to generate test recipes with nutritional information.
  - [x] Generate a test file with recipes with nutritional information.
  - [x] Load the data
  - [x] Pretty print the table with nutrition data in the markdown export
- [ ] Search for raw ingredients
- [ ] Label recipes as breakfast, lunch, dinner, snack
- [ ] Create a weekly meal plan from the recipes.
  - [ ] Generate a weekly meal plan randonmly from existing recipes.
  - [ ] Users can assign recipes to a day of the week.
  - [ ] Summary reports of nutritional values for recipes and meal plans.
- [ ] Generate a shopping list based on the meal plan.
  - [ ] The tool generates a shopping list with the required ingredients and quantities.
  - [ ] The number of people must be specified to scale the quantities correctly.
  - [ ] Shopping list displayed in the console.
- [ ] Save the shopping list to Google Keep.
  - [ ] Integration with the Google Keep API to save the shopping list directly to Google Keep.
- [ ] Edit recipes
- [ ] Check if the exception handling is well done
- [ ] Check if further tests must be written
- [ ] Are there license conflicts for new dependencies?
- [ ] Exisits a `global.json`
- [ ] Remove deactivated code
- [ ] Are all TODOs in the code done?
- [ ] Write meaningful comments
- [ ] Are there any compiler warnings?
- [ ] Do all unit tests pass in Visual Studio?
- [ ] Do all unit tests pass with `dotnet test`?
- [ ] `dotnet format Contracts.Service.sln --verify-no-changes --verbosity diagnostic`
- [ ] Is the version number correctly configured?
- [ ] Phrase a meaningful commit comment
- [ ] Check-in the changes and push them to the server
- [ ] Does the build on the buildserver succeed?
- [ ] Create a PR
- [ ] Maybe i will fill the form [openfoodfacts-python/REUSE.md at develop · openfoodfacts/openfoodfacts-python](https://github.com/openfoodfacts/openfoodfacts-python/blob/develop/REUSE.md) later

### :eyes: Review

- [ ] Initialize dev environment
- [ ] Checkout the version from Git
- [ ] Can the application be compiled?
- [ ] Are there any open warnings?
- [ ] Does the application work as a manually performed test?
- [ ] Is the layout and theme working in the UI?
- [ ] Is the UI translated?
- [ ] Is every input validated in frontend and backend?
- [ ] Are the requirements and acceptance criteria met?
- [ ] Is the code correct, clean, maintainable and well structured?
- [ ] Is the code well tested?
  - [ ] Does the test name describe the context and goal from a business perspective? What is being specified, not how it is technically implemented.
  - [ ] One aspect per test?
  - [ ] One essential assert per test. Asserts for the context should be marked as such.
  - [ ] Side-effect free and complete? No shared **instances** of objects. Especially the SUT.
  - [ ] Only fixed input data?
  - [ ] Only own code is tested?
  - [ ] Does each component have a test suite?
- [ ] Must something in README.md be updated or described?
- [ ] Does the pipeline work?
- [ ] Are there new database migrations before merging to `main`? This ensures that the database will be in the correct state after deployment.
- [ ] Shut down the dev environment

### :spiral_notepad: Notes

> [!NOTE] API
> I will use [world.openfoodfacts.org/data](https://world.openfoodfacts.org/data) as the nutritional information API. It provides free access to a large database of food products and their nutritional information. Also for european products.

[Usage - openfoodfacts-python](https://openfoodfacts.github.io/openfoodfacts-python/usage/) documents how to use the API.

With `api.product.text_search(query, page=page, page_size=page_size)` I can search for products by text. It returns a dictionary with the search results and paging information.

```python
{'count': 1956, 'page': 1, 'page_count': 1, 'page_size': 1, 'products': [...] , 'skip': 0}
```

With this information i can page through the results if needed.

The data of the products are stored in `products` in a list of dictionaries. Each dictionary contains all information about a product.

```python
{
  "_id": "4000405002377",
  "brands": "Rügenwalder,Rügenwalder Mühle",
  "product_name": "Vegane Pommersche Apfel und Zwieben",
  "quantity": "125 g",
  "nutriments": {
                "alcohol_modifier": "-",
                "carbohydrates": 8.9,
                "carbohydrates_100g": 8.9,
                "carbohydrates_unit": "g",
                "carbohydrates_value": 8.9,
                "energy": 908,
                ...
}
```

Here is some sample data:

```
Skyr Natur - Huber, Ja!, Rewe - 1pcs - Nutrients: carbohydrates: 4, carbohydrates_100g: 4, carbohydrates_serving: 6, carbohydrates_unit: g, carbohydrates_value: 4, energy: 270, energy-kcal: 64, energy-kcal_100g: 64, energy-kcal_serving: 96, energy-kcal_unit: kcal, energy-kcal_value: 64, energy-kcal_value_computed: 61.8, energy-kj: 270, energy-kj_100g: 270, energy-kj_serving: 405, energy-kj_unit: kJ, energy-kj_value: 270, energy-kj_value_computed: 262.4, energy_100g: 270, energy_serving: 405, energy_unit: kJ, energy_value: 270, fat: 0.2, fat_100g: 0.2, fat_serving: 0.3, fat_unit: g, fat_value: 0.2, fruits-vegetables-legumes-estimate-from-ingredients_100g: 0, fruits-vegetables-legumes-estimate-from-ingredients_serving: 0, fruits-vegetables-nuts-estimate-from-ingredients_100g: 0, fruits-vegetables-nuts-estimate-from-ingredients_serving: 0, nova-group: 1, nova-group_100g: 1, nova-group_serving: 1, nutrition-score-fr: -3, nutrition-score-fr_100g: -3, proteins: 11, proteins_100g: 11, proteins_serving: 16.5, proteins_unit: g, proteins_value: 11, salt: 0.08, salt_100g: 0.08, salt_serving: 0.12, salt_unit: g, salt_value: 0.08, saturated-fat: 0.1, saturated-fat_100g: 0.1, saturated-fat_serving: 0.15, saturated-fat_unit: g, saturated-fat_value: 0.1, sodium: 0.032, sodium_100g: 0.032, sodium_serving: 0.048, sodium_unit: g, sodium_value: 0.032, sugars: 4, sugars_100g: 4, sugars_serving: 6, sugars_unit: g, sugars_value: 4
```

During pagination of the nutritional information search results, I can use the `page` parameter to specify which page of results to retrieve. The `page_size` parameter allows me to define how many results should be returned per page. By adjusting these parameters, I can efficiently navigate through large sets of search results.

In the result i get the following paging information:

- `count`: Total number of products matching the search query.
- `page`: Current page number.
- `page_count`: Number of items on the current page.
- `page_size`: Number of results per page.
- `skip`: Number of results skipped (used for pagination).

Here is an example of a product in the search result:

```python
{
    'id': '4337256571074',
    'product': 'Skyr Natur',
    'brands': 'ja!',
    'quantity': '500 g',
    'energy-kcal_100g': '63.3333333333333',
    'energy-kj_100g': 270,
    'carbohydrates_100g': 4,
    'proteins_100g': 11,
    'fat_100g': '0.2',
    'sugars_100g': 4,
    'salt_100g': 0,
    'added-sugars': 0,
    'added-sugars_100g': 0,
    'added-sugars_unit': 'g',
    'added-sugars_value': 0,
    'alcohol': 0,
    'alcohol_100g': 0,
    'alcohol_serving': 0,
    'alcohol_unit': '% vol',
    'alcohol_value': 0,
    'caffeine': 0,
    'caffeine_100g': 0,
    'caffeine_unit': 'mg',
    'caffeine_value': 0,
    'calcium': 0,
    'calcium_100g': 0,
    'calcium_unit': 'mg',
    'calcium_value': 0,
    'carbohydrates': 4,
    'carbohydrates_unit': 'g',
    'carbohydrates_value': 4,
    'cholesterol': 0,
    'cholesterol_100g': 0,
    'cholesterol_unit': 'mg',
    'cholesterol_value': 0,
    'choline': 0,
    'choline_100g': 0,
    'choline_unit': 'mg',
    'choline_value': 0,
    'copper': 0,
    'copper_100g': 0,
    'copper_unit': 'mg',
    'copper_value': 0,
    'energy': 270,
    'energy-kcal': '63.3333333333333',
    'energy-kcal_unit': 'kcal',
    'energy-kcal_value': '63.3333333333333',
    'energy-kcal_value_computed': '61.8',
    'energy-kj': 270,
    'energy-kj_unit': 'kJ',
    'energy-kj_value': 270,
    'energy-kj_value_computed': '262.4',
    'energy_100g': 270,
    'energy_unit': 'kJ',
    'energy_value': 270,
    'fat': '0.2',
    'fat_unit': 'g',
    'fat_value': '0.2',
    'fiber': 0,
    'fiber_100g': 0,
    'fiber_unit': 'g',
    'fiber_value': 0,
    'fruits-vegetables-legumes-estimate-from-ingredients_100g': 0,
    'fruits-vegetables-legumes-estimate-from-ingredients_serving': 0,
    'fruits-vegetables-nuts-estimate-from-ingredients_100g': 0,
    'fruits-vegetables-nuts-estimate-from-ingredients_serving': 0,
    'iron': 0,
    'iron_100g': 0,
    'iron_unit': 'mg',
    'iron_value': 0,
    'magnesium': 0,
    'magnesium_100g': 0,
    'magnesium_unit': 'mg',
    'magnesium_value': 0,
    'manganese': 0,
    'manganese_100g': 0,
    'manganese_unit': 'mg',
    'manganese_value': 0,
    'monounsaturated-fat': 0,
    'monounsaturated-fat_100g': 0,
    'monounsaturated-fat_unit': 'g',
    'monounsaturated-fat_value': 0,
    'nova-group': 1,
    'nova-group_100g': 1,
    'nova-group_serving': 1,
    'nutrition-score-fr': -3,
    'nutrition-score-fr_100g': -3,
    'phosphorus': 0,
    'phosphorus_100g': 0,
    'phosphorus_unit': 'mg',
    'phosphorus_value': 0,
    'polyunsaturated-fat': 0,
    'polyunsaturated-fat_100g': 0,
    'polyunsaturated-fat_unit': 'g',
    'polyunsaturated-fat_value': 0,
    'potassium': 0,
    'potassium_100g': 0,
    'potassium_unit': 'mg',
    'potassium_value': 0,
    'proteins': 11,
    'proteins_unit': 'g',
    'proteins_value': 11,
    'salt': 0,
    'salt_unit': 'mg',
    'salt_value': 0,
    'saturated-fat': '0.133333333333333',
    'saturated-fat_100g': '0.133333333333333',
    'saturated-fat_unit': 'g',
    'saturated-fat_value': '0.133333333333333',
    'selenium': 0,
    'selenium_100g': 0,
    'selenium_unit': 'mcg',
    'selenium_value': 0,
    'sodium': 0,
    'sodium_100g': 0,
    'sodium_unit': 'mg',
    'sodium_value': 0,
    'starch': 0,
    'starch_100g': 0,
    'starch_unit': 'g',
    'starch_value': 0,
    'sugars': 4,
    'sugars_unit': 'g',
    'sugars_value': 4,
    'trans-fat': 0,
    'trans-fat_100g': 0,
    'trans-fat_unit': 'g',
    'trans-fat_value': 0,
    'vitamin-a': 0,
    'vitamin-a_100g': 0,
    'vitamin-a_unit': 'mcg',
    'vitamin-a_value': 0,
    'vitamin-b1': 0,
    'vitamin-b12': 0,
    'vitamin-b12_100g': 0,
    'vitamin-b12_unit': 'mcg',
    'vitamin-b12_value': 0,
    'vitamin-b1_100g': 0,
    'vitamin-b1_unit': 'mg',
    'vitamin-b1_value': 0,
    'vitamin-b2': 0,
    'vitamin-b2_100g': 0,
    'vitamin-b2_unit': 'mg',
    'vitamin-b2_value': 0,
    'vitamin-b6': 0,
    'vitamin-b6_100g': 0,
    'vitamin-b6_unit': 'mg',
    'vitamin-b6_value': 0,
    'vitamin-b9': 0,
    'vitamin-b9_100g': 0,
    'vitamin-b9_unit': 'mcg',
    'vitamin-b9_value': 0,
    'vitamin-c': 0,
    'vitamin-c_100g': 0,
    'vitamin-c_unit': 'mg',
    'vitamin-c_value': 0,
    'vitamin-d': 0,
    'vitamin-d_100g': 0,
    'vitamin-d_unit': 'mcg',
    'vitamin-d_value': 0,
    'vitamin-e': 0,
    'vitamin-e_100g': 0,
    'vitamin-e_unit': 'mg',
    'vitamin-e_value': 0,
    'vitamin-k': 0,
    'vitamin-k_100g': 0,
    'vitamin-k_unit': 'mcg',
    'vitamin-k_value': 0,
    'zinc': 0,
    'zinc_100g': 0,
    'zinc_unit': 'mg',
    'zinc_value': 0
}
```

Error during calculation of nutrition for recipes because of 'N/A' values:

```
2026-01-09 12:56:47,763 | ERROR | An error of type <class 'ValueError'> occurred. Message: could not convert string to float: 'N/A'
Traceback (most recent call last):
  File "C:\Dev\python_workshop_project\src\main.py", line 24, in <module>
    recipe_cli.CommandLineHandler().show()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Dev\python_workshop_project\src\recipes\command_line_handler.py", line 36, in show
    command = self._add_recipe()
  File "C:\Dev\python_workshop_project\src\recipes\command_line_handler.py", line 194, in _add_recipe
    _add_ingredients_to(recipe)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "C:\Dev\python_workshop_project\src\recipes\command_line_handler.py", line 119, in _add_ingredients_to
    recipe.add_ingredient((int(amount), food))
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Dev\python_workshop_project\src\recipes\recipe.py", line 21, in add_ingredient
    self.nutrition = self._calculate_nutrition()
                     ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Dev\python_workshop_project\src\recipes\recipe.py", line 74, in _calculate_nutrition
    nutrition["energy"] += float(ingredient.get("energy-kj_100g", 0)) * factor
                           ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: 'N/A'
```

> [!TIP] Paging
> I just have to name the page until `skip` + `page_count` = `count`.

> [!NOTE]
> This is a note

> [!TIP]
> This is a tip.

> [!WARNING]
> This is a warning

> [!IMPORTANT]
> This info is important to know.

> [!CAUTION]
> This has possibly negative consequences.

## :mag: Debug

- [ ] ID: 🟢🔴🟡 Result: As Expected

## :books: Documentation
- [ ] Do I need a new PIA or update an existing one?
- [ ] Update the README.md
- [ ] Update the CHANGELOG.md
- [ ] Describe the setup of the story if needed for end users
- [ ] Does something in the wiki needed to be updated?
- [ ] Needs other stuff been documented?

### :bulb: Decisions

| Decision          | Cause                      |
| ----------------- | -------------------------- |
| What was decided? | Why was the decision made? |

### :page_facing_up: PIAs

Link to related PIA

### :link: Links

#### Libs
- [questionary](https://github.com/tmbo/questionary)
- [Questionary — Questionary 2.0.1 documentation](https://questionary.readthedocs.io/en/stable/index.html)
- [rich](https://github.com/Textualize/rich)
- [Tables — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/tables.html)
- [Layout — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/layout.html)

#### APIs
- [The Largest Global Nutrition Database, Recipe and Food API | fatsecret Platform](https://platform.fatsecret.com/platform-api)
- [world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
- [Usage - openfoodfacts-python](https://openfoodfacts.github.io/openfoodfacts-python/usage/)
- [openfoodfacts.github.io/openfoodfacts-server/api/ref-v3/](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-v3/)

## :clapper: Demo

- [ ] Setup a fresh demo environment
- [ ] Check all acceptance tests

## :package: Deployment

- [ ] Merge `feature` into `main` or `hotfix` into `production` and `main` and remove the `feature` branch
- [ ] Check if the compiled artifact is valid
- [ ] Cleanup the Git history locally on the dev system

## :beer: Retro

> [!TIP]  Was gab es zu lernen?
> What did I learn?

> [!WARNING] Where were the problems?
> Where did I have difficulties? What hindered my work?

## :unicorn: Magie

Hints and tricks that were helpful during the implementation or documentation.

<details>
    <summary>Emojis to label information</summary>

| Emoji                | Bedeutung                 |
| :------------------- | :------------------------ |
| :x:                  | Nein                      |
| :ok:                 | Ja                        |
| :warning:            | Achtung                   |
| :information_source: | Zusätzliche Informationen |
| :zzz:                | Wartet                    |
| :red_circle:         | Fehlschlag                |
| :green_circle:       | Erfolg                    |
| :yellow_circle:      | Problem                   |
</details>

<details> 
    <summary>PR</summary>

A PR needs a title that lets the reviewer recognize which ticket it belongs to. The format is:

`#<issue number> <issue title>`

It helps the reviewer if you provide details about the development environment. Breaking changes in services can make it unclear which versions of services the reviewer should use for the review.

The versions can be set up from artefacts or via Git by using the correct branches.

If the exact version is not critical, it may be sufficient to simply use the image with latest.

Here is a template for a PR:

```markdown
## Notes

BREAKING CHANGE: Is this a breaking change?

Is there anything special to note? Perhaps deviations from the ticket or details that came up during development?

## Changes

- Fixed a typo
- Optimized code
- New feature XYZ

## Development environment

### Versions

| Application | Version |
| :---------- | ------: |
| Client      |   1.5.0 |
| Service     |   1.2.4 |
| KeyCloak    |  latest |
| Postgres    |  latest |

### Setup

Scripts or test data used? Ideally attach or link it.
```
</details>

<details>
    <summary>Database migration with EF Core</summary>

```powershell
PS> cd .\src\ProjectName
PS> dotnet ef database update
PS> dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj
```

`dotnet ef` can be updated with the command `dotnet tool update -g dotnet-ef --version 7.0.14`.

During development, sometimes it is necessary to recreate a migration:

```powershell
# List all migrations an copy the one to reset the database to.
dotnet ef migrations list

dotnet ef database update <migration_name> && dotnet ef migrations remove && dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj && dotnet ef database update
```

> [!WARNING] ATTENTION
> Before merging into `main`, you must check if there are new migrations. The best way to do this is by comparing the migrations in `main` with those in your own branch. It is a good idea to commit migrations separately so that they can be easily reverted if necessary.

If there are new migrations on `main`, proceed as follows:

1. With the feature branch, reset the database to the last state before your own migration. `dotnet ef database update <migration_name>`
2. On the feature branch, remove the last commit with a `reset`.
3. Merge `main`.
4. Now create a new migration. `dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj && dotnet ef database update`
5. Commit the migration.
</details>