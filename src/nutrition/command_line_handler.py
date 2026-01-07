import logging
import questionary
import nutrition.repository as nutrition_repository
from prompt_toolkit.formatted_text import FormattedText
from config.console import console, print_info, print_rule_separated

log = logging.getLogger(__name__)


class CommandLineHandler:
    NUTRITION_SEARCH_TERM_COMMAND = "NUTRITION_SEARCH_TERM_COMMAND"
    CANCEL_COMMAND = "CANCEL_COMMAND"
    PREVIOUS_COMMAND = "PREVIOUS_COMMAND"
    NEXT_COMMAND = "NEXT_COMMAND"

    def show(self):
        """
        Displays the command line interface to the user and handles input.
        """

        command, search_term = self._get_nutrition_search_term()

        if command == self.CANCEL_COMMAND:
            return  # User chose to cancel; return to main menu.

        if command == self.NUTRITION_SEARCH_TERM_COMMAND:
            result = self._execute_search(search_term)

            if result is None or result == self.CANCEL_COMMAND:
                return  # User chose to cancel during search; return to main menu.
            else:
                console.print(result)  # Display the selected product details.

    def _get_nutrition_search_term(self):
        """
        Prompts the user to enter a search term for nutritional information.

        :return: The search term entered by the user with the search nutrition command or a cancel command if none is entered or CTRL+C is pressed.
        """

        search_term = questionary.text(
            "What food product do you want to search for?"
        ).ask()

        if search_term is None or search_term.strip() == "":
            log.warning("No search term entered. Returning to main menu.")
            return (self.CANCEL_COMMAND, None)

        return (self.NUTRITION_SEARCH_TERM_COMMAND, search_term.strip())

    def _execute_search(self, search_term: str, page: int = 1):
        """
        Executes the nutrition search using the provided search term and handles pagination.

        :param search_term: The term to search for in the nutrition repository.
        :param page: The page number to retrieve.
        :return: The selected product, next/previous command, or cancel command.
        """

        with console.status("Searching...", spinner="earth"):
            # Don't change the page_size to more than 7. The index is used for shortcut
            # keys and more than 9 items would break it.
            search_result = nutrition_repository.NutritionRepository().search_products(
                search_term, page=page, page_size=7
            )

        product_count = search_result["count"]

        if product_count == 0:
            print_info(
                f"No products found for search term: '[yellow]{search_term}[/yellow]'"
            )
        else:
            print_rule_separated(
                f"Showing {search_result['skip'] + 1} to {search_result['skip'] + search_result['page_count']} of {product_count} products for search term: '{search_term}'"
            )

            choices = []
            self._add_navigation_choices_to_menu(choices, search_result, product_count)
            self._add_item_choices_to_menu(choices, search_result)

            selection = questionary.select(
                "Select a product to view details:",
                choices=choices,
                use_shortcuts=True,
            ).ask()

            if selection == self.PREVIOUS_COMMAND:
                return self._execute_search(search_term, page=page - 1)

            if selection == self.NEXT_COMMAND:
                return self._execute_search(search_term, page=page + 1)

            return selection  # Return the selected product or cancel command

    def _add_navigation_choices_to_menu(self, choices, products, product_count):
        """
        Adds pagination and cancel choices to the list of choices.

        :param choices: The current list of choices.
        :param products: The products search results.
        :param product_count: The total number of products.
        """

        has_next_page = products["skip"] + products["page_count"] < product_count
        has_previous_page = products["skip"] > 0

        choices += [
            questionary.Choice(
                title=FormattedText(
                    [
                        (
                            "",  # No special style
                            f"{0}) ",  # Shortcut key 0
                        ),
                        (
                            "bold fg:ansired ",
                            "Cancel",
                        ),
                    ]
                ),
                value=self.CANCEL_COMMAND,
                shortcut_key=str(0),  # Assign shortcut key '0' to Cancel
            ),
            questionary.Choice(
                title=FormattedText(
                    [
                        (
                            f"{'fg:ansiblue' if has_previous_page else 'fg:ansibrightblack'} ",
                            f"{1}) ",  # Shortcut key 1
                        ),
                        (
                            f"bold {'fg:ansiblue' if has_previous_page else 'fg:ansibrightblack'} ",
                            "Previous",
                        ),
                    ]
                ),
                value=self.PREVIOUS_COMMAND,
                shortcut_key=str(1),  # Assign shortcut key '1' to Previous
                disabled=not has_previous_page,
            ),
            questionary.Choice(
                title=FormattedText(
                    [
                        (
                            f"{'fg:ansigreen' if has_next_page else 'fg:ansibrightblack'} ",
                            f"{2}) ",  # Shortcut key 2
                        ),
                        (
                            f"bold {'fg:ansigreen' if has_next_page else 'fg:ansibrightblack'} ",
                            "Next",
                        ),
                    ]
                ),
                value=self.NEXT_COMMAND,
                shortcut_key=str(2),  # Assign shortcut key '2' to Next
                disabled=not has_next_page,
            ),
        ]

    def _add_item_choices_to_menu(self, choices, products):
        """
        Adds product item choices to the list of choices.

        :param choices: The current list of choices.
        :param products: The products search results.
        """

        for index, product in enumerate(products["products"], start=3):
            choices.append(
                questionary.Choice(
                    title=FormattedText(
                        [
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
                        ]
                    ),
                    value=product,
                    shortcut_key=str(index),  # Assign shortcut key based on index
                )
            )
