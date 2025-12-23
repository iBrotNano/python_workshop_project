import logging
import questionary
import nutrition.repository as nutrition_repository

log = logging.getLogger(__name__)


class CommandLineHandler:
    NUTRITION_SEARCH_TERM_COMMAND = "NUTRITION_SEARCH_TERM_COMMAND"
    CANCEL_COMMAND = "CANCEL_COMMAND"

    def show(self):
        """
        Displays the command line interface to the user and handles input.
        """

        command, search_term = self._get_nutrition_search_term()

        if command == self.CANCEL_COMMAND:
            return  # User chose to cancel; return to main menu.

        if command == self.NUTRITION_SEARCH_TERM_COMMAND:
            self._execute_search(search_term)

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

    def _execute_search(self, search_term: str):
        """
        Executes the nutrition search using the provided search term.

        :param search_term: The term to search for in the nutrition repository.
        """

        products = nutrition_repository.NutritionRepository().search_products(
            search_term, page=1
        )

        if not products:
            print(f"No products found for search term: '{search_term}'")
        else:
            print(
                f"Found {products['count']} products for search term: '{search_term}'"
            )

            choices = []

            for product in products["products"]:
                choices.append(
                    questionary.Choice(
                        title=f"{product['product']}",  # TODO: enhance with more details
                        value=product,
                    )
                )

            questionary.select(
                "Select a product to view details:", choices=choices, use_shortcuts=True
            ).ask()
