import logging
import questionary

from typing import Any
from rich.table import Table
from common.terminal import terminal
from config.configuration import configuration
from nutrition.prompt import Prompt
from rich.markdown import Markdown

log = logging.getLogger(__name__)


class CommandLineHandler:
    """Handles the command line interface for nutrition-related features."""

    QUESTION_COMMAND = "QUESTION"
    CANCEL_COMMAND = "CANCEL"
    # PREVIOUS_COMMAND = "PREVIOUS"
    # NEXT_COMMAND = "NEXT"

    def show(self):
        """
        Displays the command line interface to the user and handles input.

        :param self: This instance of the CommandLineHandler class.
        """

        command, question = self._get_question()

        if command == self.CANCEL_COMMAND:
            return  # User chose to cancel; return to main menu.

        if command == self.QUESTION_COMMAND and question is not None:
            result = self._prompt(question)

            if result is None or result == self.CANCEL_COMMAND:
                return  # User chose to cancel during search; return to main menu.
            elif isinstance(result, dict):
                self._print_nutrition_info(result)
                return result

    def _get_question(self) -> tuple[str, str | None]:
        """
        Prompts the user to enter a question about nutritional information.

        :param self: This instance of the CommandLineHandler class.

        :return: The search term entered by the user with the search nutrition command or a cancel command if none is entered or CTRL+C is pressed.
        :rtype: tuple[str, str | None]
        """

        question = terminal.safe_text("How can I help you?")

        if question is None or type(question) is not str or question.strip() == "":
            terminal.print_info("Nothing asked.")
            return (self.CANCEL_COMMAND, None)

        return (self.QUESTION_COMMAND, question.strip())

    def _prompt(self, query: str) -> dict | str | None:
        """
        Executes the nutrition chat using the provided query and keeps the conversation open.

        :param self: This instance of the CommandLineHandler class.
        :param query: The term to search for in the nutrition repository.
        :type search_term: str
        :return: The selected product, next/previous command, or cancel command.
        :rtype: dict | str | None
        """

        messages: list[dict[str, Any]] | None = None

        while True:
            prompt = Prompt(configuration)
            response, _search_result, messages = prompt.execute(query, 9, messages)
            terminal.print(Markdown(response))
            command, next_query = self._get_question()

            if command == self.CANCEL_COMMAND:
                return self.CANCEL_COMMAND

            if next_query is not None:
                query = next_query

        # TODO: Implement the selection part
        # product_count = search_result["count"]
        # product_count = len(search_result)

        # if product_count == 0:
        #     terminal.print_info(f"No products found!")
        # else:
        #     # terminal.print_rule_separated(
        #     #     f"Showing {search_result['skip'] + 1} to {search_result['skip'] + search_result['page_count']} of {product_count} products for search term: '{search_term}'"
        #     # )

        #     choices = []
        #     self._add_navigation_choices_to_menu(choices, search_result, product_count)
        # self._add_item_choices_to_menu(choices, search_result)

        # selection = questionary.select(
        #     "Select a product to view details:",
        #     choices=choices,
        #     use_shortcuts=True,
        # ).ask()

        # if selection == self.PREVIOUS_COMMAND:
        #     return self._execute_search(search_term, page=page - 1)

        # if selection == self.NEXT_COMMAND:
        #     return self._execute_search(search_term, page=page + 1)

        # return selection  # Return the selected product or cancel command

    def _add_navigation_choices_to_menu(self, choices, products, product_count):
        """
        Adds pagination and cancel choices to the list of choices.

        :param choices: The current list of choices.
        :param products: The products search results.
        :param product_count: The total number of products.
        """

        # has_next_page = products["skip"] + products["page_count"] < product_count
        # has_previous_page = products["skip"] > 0

        choices += [
            questionary.Choice(
                title=[
                    (
                        "",  # No special style
                        f"{0}) ",  # Shortcut key 0
                    ),
                    (
                        "bold fg:ansired ",
                        "Cancel",
                    ),
                ],
                value=self.CANCEL_COMMAND,
                shortcut_key=str(0),  # Assign shortcut key '0' to Cancel
            ),
            # questionary.Choice(
            #     title=[
            #         (
            #             f"{'fg:ansiblue' if has_previous_page else 'fg:ansibrightblack'} ",
            #             f"{1}) ",  # Shortcut key 1
            #         ),
            #         (
            #             f"bold {'fg:ansiblue' if has_previous_page else 'fg:ansibrightblack'} ",
            #             "Previous",
            #         ),
            #     ],
            #     value=self.PREVIOUS_COMMAND,
            #     shortcut_key=str(1),  # Assign shortcut key '1' to Previous
            #     disabled=None if has_previous_page else "No previous page",
            # ),
            # questionary.Choice(
            #     title=[
            #         (
            #             f"{'fg:ansigreen' if has_next_page else 'fg:ansibrightblack'} ",
            #             f"{2}) ",  # Shortcut key 2
            #         ),
            #         (
            #             f"bold {'fg:ansigreen' if has_next_page else 'fg:ansibrightblack'} ",
            #             "Next",
            #         ),
            #     ],
            #     value=self.NEXT_COMMAND,
            #     shortcut_key=str(2),  # Assign shortcut key '2' to Next
            #     disabled=None if has_next_page else "No next page",
            # ),
        ]

    def _add_item_choices_to_menu(self, choices, products):
        """
        Adds product item choices to the list of choices.

        :param choices: The current list of choices.
        :param products: The products search results.
        """

        for index, product in enumerate(products, start=1):
            choices.append(
                questionary.Choice(
                    title=[
                        (
                            "",  # No special style
                            f"{index}) ",  # Shortcut key
                        ),
                        (
                            "bold fg:ansiyellow ",
                            f"{product['brands']} {product['product']} {product['quantity']}",
                        ),
                        (
                            "fg:ansibrightblack ",
                            f" | {product['energy-kcal_100g']} kcal / {product['energy-kj_100g']} kj | {product['carbohydrates_100g']} g carbs | {product['proteins_100g']} g proteins | {product['fat_100g']} g fat | {product['sugars_100g']} g sugars | {product['salt_100g']} g salt",
                        ),
                    ],
                    value=product,
                    shortcut_key=str(index),  # Assign shortcut key based on index
                )
            )

    def _print_nutrition_info(self, product: dict):
        """
        Prints the nutritional information of the product in a table format.

        :param self: This instance of the CommandLineHandler class.
        :param product: The product details.
        :type product: dict
        """

        def _print_nutrition_table(
            nutrients: dict[str, str],
            column1_title: str,
            column2_title: str,
        ):
            """
            Display nutritional information in a formatted table.
            Creates and prints a Rich table containing nutrient names and their
            amounts per 100g of product. The table uses colored columns for
            better readability in console output.

            :param nutrients: A dictionary mapping nutrient names (str) to their amounts (str).
            :param column1_title: The title for the first column.
            :param column2_title: The title for the second column.
            """

            table = Table()
            table.add_column(column1_title, style="cyan", no_wrap=True)
            table.add_column(column2_title, style="magenta")

            for nutrient, amount in nutrients.items():
                table.add_row(nutrient, str(amount))

            terminal.print(table)

        terminal.print_rule_separated(
            f"[link={product['url']}]{product['brands']} {product['product']} {product['quantity']}[/link]"
        )

        # Print essential nutrients table
        _print_nutrition_table(
            {
                "Energy": f"{product['energy-kcal_100g']} kcal / {product['energy-kj_100g']} kj",
                "Carbohydrates": f"{product['carbohydrates_100g']} {product['carbohydrates_unit']}",
                "Proteins": f"{product['proteins_100g']} {product['proteins_unit']}",
                "Fat": f"{product['fat_100g']} {product['fat_unit']}",
                "Sugars": f"{product['sugars_100g']} {product['sugars_unit']}",
                "Salt": f"{product['salt_100g']} {product['salt_unit']}",
            },
            column1_title="Nutrient",
            column2_title="Amount per 100g",
        )

        # Print additional nutrients table
        # Get all data from structure like this:
        # 'vitamin-k_100g': 0, used as key
        # 'vitamin-k_unit': 'mcg' used to get unit
        _print_nutrition_table(
            {
                nutrient.replace("_100g", "")
                .replace("-", " ")
                .title(): f"{value} {product.get(nutrient.replace('_100g', '_unit'), '')}"
                for nutrient, value in product.items()
                if nutrient.endswith("_100g")
                and nutrient
                not in [
                    "energy-kcal_100g",
                    "energy-kj_100g",
                    "carbohydrates_100g",
                    "proteins_100g",
                    "fat_100g",
                    "sugars_100g",
                    "salt_100g",
                ]
            },
            column1_title="Info",
            column2_title="Unit per 100g",
        )
