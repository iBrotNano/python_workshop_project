import logging
import questionary
from recipes import recipe_types
from recipes.recipe import Recipe
from recipes.repository import Repository
from config.console import console
from common.console import print_rule_separated, print_dict_as_table, print_info
import nutrition.command_line_handler as nutrition_cli
from rich.markdown import Markdown

log = logging.getLogger(__name__)


class CommandLineHandler:
    CANCEL_COMMAND = "CANCEL"
    ADD_RECIPE_COMMAND = "ADD_RECIPE"
    DELETE_RECIPE_COMMAND = "DELETE_RECIPE"
    VIEW_RECIPE_COMMAND = "VIEW_RECIPE"

    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        """
        self.repository = Repository()

    def show(self):
        """
        Displays the command line interface to the user and handles input.
        """
        while True:
            command = self._get_recipe_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return  # User chose to cancel; return to main menu.

            if command == self.VIEW_RECIPE_COMMAND:
                self._view_recipe()

            if command == self.ADD_RECIPE_COMMAND:
                command = self._add_recipe()

                if command == self.CANCEL_COMMAND:
                    self.show()  # Return to recipe menu.
                    return

            if command == self.DELETE_RECIPE_COMMAND:
                self._delete_recipe()

    def _get_recipe_menu_selection(self):
        """
        Displays the menu and gets the user's selection.

        :return: The command selected by the user.
        """

        choices = [
            questionary.Choice(
                "View recipe",
                value=self.VIEW_RECIPE_COMMAND,
            ),
            questionary.Choice(
                "Add recipe",
                value=self.ADD_RECIPE_COMMAND,
            ),
            questionary.Choice(
                "Delete recipe",
                value=self.DELETE_RECIPE_COMMAND,
            ),
            questionary.Choice(
                "Back to main menu",
                value=self.CANCEL_COMMAND,
            ),
        ]

        return questionary.select(
            "What do you want to do?", choices=choices, use_shortcuts=True
        ).ask()

    def _add_recipe(self):
        """
        Handles the process of adding a new recipe.
        """

        def _enter_recipe_name_to(recipe: Recipe):
            """
            Prompts the user to enter a recipe name as long as they want to try.

            :param recipe: The recipe to name.
            :type recipe: Recipe
            """
            recipe.name = questionary.text(
                "What is the name of the recipe you want to add?"
            ).ask()

            # A recipe needs at least a name to store something meaningful.
            if recipe.name is None or recipe.name.strip() == "":
                log.warning("No recipe name entered. Returning to menu.")
                return self.CANCEL_COMMAND
            else:
                if not self.repository.try_add(recipe):
                    log.warning(
                        f"A recipe with the name '{recipe.name}' already exists."
                    )

                    if questionary.confirm(
                        "Do you want to try a different name?"
                    ).ask():
                        return _enter_recipe_name_to(recipe)
                    else:
                        return self.CANCEL_COMMAND

        def _select_recipe_type(recipe: Recipe):
            """
            Prompts the user to select a recipe type.

            :param recipe: The recipe to set the type for.
            :type recipe: Recipe
            """
            choices = [
                questionary.Choice(
                    recipe_types.BREAKFAST.capitalize(), value=recipe_types.BREAKFAST
                ),
                questionary.Choice(
                    recipe_types.LUNCH.capitalize(), value=recipe_types.LUNCH
                ),
                questionary.Choice(
                    recipe_types.DINNER.capitalize(), value=recipe_types.DINNER
                ),
                questionary.Choice(
                    recipe_types.SNACK.capitalize(), value=recipe_types.SNACK
                ),
            ]

            recipe.type = questionary.select(
                "Select the type of the recipe:",
                choices=choices,
                use_shortcuts=True,
            ).ask()

            if not recipe.type:
                log.warning("No recipe type selected. Returning to menu.")
                return self.CANCEL_COMMAND

        def _add_ingredients_to(recipe: Recipe):
            """
            Prompts the user to add an ingredient to the recipe.

            :param recipe: The recipe to add the ingredient to.
            :type recipe: Recipe
            """
            while True:
                food = food_search.show()

                if food:
                    if questionary.confirm(
                        "Do you want to add this to your recipe?"
                    ).ask():
                        amount = questionary.text(
                            "Enter an amount in grams per person:",
                            default="100",
                            validate=lambda text: text.isdigit()
                            or "Please enter a valid number",
                        ).ask()

                        if amount:
                            recipe.add_ingredient((int(amount), food))

                            # Only show the table if there are ingredients.
                            print_dict_as_table(
                                {
                                    f"[link={ingredient['url']}]{ingredient['brands']} {ingredient['product']}[/link]": f"{amount}g"
                                    for amount, ingredient in recipe.ingredients
                                },
                                "Ingredients",
                                "Amount in g per person",
                            )

                            print_dict_as_table(
                                recipe.get_formatted_nutrition(),
                                "Nutrition",
                                "Amount per person",
                            )

                if not questionary.confirm(
                    "Do you want to add another ingredient to your recipe?"
                ).ask():
                    break

            console.print(
                f"Recipe '{recipe.name}' added with {len(recipe.ingredients)} ingredients."
            )

        def _add_instructions_to(recipe: Recipe):
            """
            Prompts the user to add instructions to the recipe.

            :param recipe: The recipe to add instructions to.
            :type recipe: Recipe
            """

            instructions = questionary.text(
                "Enter the instructions for the recipe (multiline):",
                multiline=True,
            ).ask()

            if instructions:
                recipe.instructions = instructions
                console.print(f"Instructions added to recipe '{recipe.name}'.")

        def _save(recipe: Recipe):
            """
            Saves the recipe with the repository.

            :param recipe: The recipe to save.
            :type recipe: Recipe
            """
            if questionary.confirm(
                f"Do you want to save the recipe '{recipe.name}' to disk?"
            ).ask():
                self.repository.save()
                console.print(f"Recipe '{recipe.name}' saved to disk.")
            else:
                if questionary.confirm(
                    f"Do you really want to discard the recipe '{recipe.name}'? All data will be lost."
                ).ask():
                    del self.repository.recipes[recipe.name]
                    console.print(f"Recipe '{recipe.name}' discarded.")
                else:
                    _save(recipe)

        recipe = Recipe()

        if _select_recipe_type(recipe) == self.CANCEL_COMMAND:
            return self.CANCEL_COMMAND

        if _enter_recipe_name_to(recipe) == self.CANCEL_COMMAND:
            return self.CANCEL_COMMAND

        print_rule_separated("Your recipe needs some ingredients. Let's add them now!")
        food_search = nutrition_cli.CommandLineHandler()
        _add_ingredients_to(recipe)
        _add_instructions_to(recipe)
        md = Markdown(recipe.as_markdown())
        console.print(md, width=100)
        _save(recipe)

    def _delete_recipe(self):
        """
        Deletes a recipe from the repository.
        """
        recipe_name = self._select_recipe_with_autocomplete()

        if recipe_name:
            if questionary.confirm(
                f"Are you sure you want to delete the recipe '{recipe_name}'?"
            ).ask():
                self.repository.delete(recipe_name)
                print_info(f"Recipe '{recipe_name}' has been deleted.")

    def _view_recipe(self):
        """
        Views a recipe from the repository.
        """

        recipe_name = self._select_recipe_with_autocomplete()

        if recipe_name:
            recipe = self.repository.get(recipe_name)
            md = Markdown(recipe.as_markdown())
            console.print(md, width=100)

            if questionary.confirm("Do you want to export the recipe?").ask():
                file_name = questionary.path(
                    "Where do you want to save the markdown file?",
                    only_directories=True,
                    default=f"export\\{recipe.name.replace(' ', '_')}.md",
                ).ask()

                if file_name:
                    recipe.export_as_markdown(file_name)
                    print_info(f"Recipe exported to '{file_name}'.")

    def _select_recipe_with_autocomplete(self):
        """
        Prompts the user to select a recipe using autocomplete.

        :param prompt: The prompt to display to the user.
        :return: The selected recipe name or None if cancelled.
        """
        if not self.repository.recipes:
            print_info("No recipes available to view.")
            return

        return questionary.autocomplete(
            "Select the recipe you want to view:",
            choices=list(self.repository.recipes.keys()),
            ignore_case=True,
            validate=lambda text: text
            in self.repository.recipes.keys()  # Only exiting names are valid
            or "Please select a valid recipe name from the list.",
        ).ask()
