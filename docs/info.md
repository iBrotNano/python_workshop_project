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
- [ ] I will test that the app exits when I type "exit". Spaces before and after "exit" should be ignored, and the command should be case-insensitive.
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

### Nutritional information API

An existing API will be queried to get nutritional information. The app will handle user input via the command line and display output in the console.

## :microscope: Dissection

| Integration test | 1                                                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will exit the app by typing "exit" (case insensitive, ignoring leading/trailing spaces) where a text prompt appears.       |
| Test cases       | `exit`, ` EXIT `, `ExIt`                                                                                                     |
| Expected result  | The app should terminate gracefully without errors. The command is always recognized, no matter in what state the app is in. |

| Integration test | 2                                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| Action           | I will provoke an error by not configuring something important.                                      |
| Expected result  | The errors are handled gracefully and the app does not crash. The error is displayed in the console. |

| Integration test | 3                                                                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Action           | I will provoke an error by not configuring something important.                                                                     |
| Expected result  | A logfile is created with detailed error information for debugging purposes. The error details include timestamps and stack traces. |

| Integration test | 4                                                   |
| ---------------- | --------------------------------------------------- |
| Action           | I will exit the app via the main menu.              |
| Expected result  | The app should terminate gracefully without errors. |

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

## :hammer_and_wrench: Development

### :clipboard: TODOs

- [x] Exit the app when the user types "exit" (case insensitive, ignoring leading/trailing spaces)
- [x] Handle all errors gracefully with appropriate messages in the console
- [x] Timestamp for error logging in the console
- [x] Log all errors into a log file with timestamps for debugging purposes
- [x] Use Lib for input to make app handling easier
- [x] Add menue to select between the main functions and exit
- [x] Ask for confirmation before exiting the app
- [ ] Development of a simple CLI tool to query nutritional information from an API (https://publicapis.io/open-food-facts-api, https://platform.fatsecret.com/platform-api). Search for foods and display nutrition facts.
  - [x] Make the name of my app configurable
  - [x] Make the version of my app configurable
  - [ ] Check the API [world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
    - [x] Inspect the returned data structure
    - [ ] Implement the test code from `main.py` into the repository class
    - [ ] Delete `api_call.py`
  - [ ] Configuration settings for API access and user preferences.
  - [ ] Search criteria are name and manufacturer.
  - [ ] Search results from the API displayed in the console.
  - [ ] Nutritional values of recipes displayed in the console.
- [ ] Create recipes with nutrition calculation.
  - [ ] Users can enter recipes, and the tool calculates the overall nutritional values based on the ingredients.
  - [ ] Ingredients are selected via product search. Ingredient quantities in the recipe must be specified, optionally with the number of people the recipe is intended for.
  - [ ] Recipes are saved as a JSON file and can be loaded again later. (Maybe YAML?) How to input recipe instuctions?
  - [ ] Quantity information is persisted per person.
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

#### APIs
- [The Largest Global Nutrition Database, Recipe and Food API | fatsecret Platform](https://platform.fatsecret.com/platform-api)
- [world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
- [Usage - openfoodfacts-python](https://openfoodfacts.github.io/openfoodfacts-python/usage/)

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