import logging
import questionary

from dataclasses import fields
from rich.table import Table
from sqlite_rag.models.document_result import DocumentResult
from common.terminal.terminal import terminal
from nutrition.nutrition import Nutrition
from nutrition.nutrition_repository import NutritionRepository
from persistence.database_engine_factory import database_engine
from persistence.retriever_manager import retriever_manager
from config.configuration import configuration

log = logging.getLogger(__name__)


class CommandLineHandler:
    """Handles the command line interface for nutrition-related features."""

    NUTRITION_SEARCH_TERM_COMMAND = "NUTRITION_SEARCH_TERM"
    CANCEL_COMMAND = "CANCEL"

    def show(self):
        """
        Displays the command line interface to the user and handles input.

        :param self: This instance of the CommandLineHandler class.
        """

        command, search_term = self._get_nutrition_search_term()

        if command == self.CANCEL_COMMAND:
            return  # User chose to cancel; return to main menu.

        if command == self.NUTRITION_SEARCH_TERM_COMMAND and search_term is not None:
            result = self._execute_search(search_term)

            if result is None or result == self.CANCEL_COMMAND:
                return  # User chose to cancel during search; return to main menu.
            elif isinstance(result, Nutrition):
                self._print_nutrition_info(result)
                return result

    def _get_nutrition_search_term(self) -> tuple[str, str | None]:
        """
        Prompts the user to enter a search term for nutritional information.

        :param self: This instance of the CommandLineHandler class.

        :return: The search term entered by the user with the search nutrition command or a cancel command if none is entered or CTRL+C is pressed.
        :rtype: tuple[str, str | None]
        """

        search_term = terminal.safe_text("What food product do you want to search for?")

        if (
            search_term is None
            or type(search_term) is not str
            or search_term.strip() == ""
        ):
            terminal.print_info("No search term entered.")
            return (self.CANCEL_COMMAND, None)

        return (self.NUTRITION_SEARCH_TERM_COMMAND, search_term.strip())

    def _execute_search(self, search_term: str) -> Nutrition | str | None:
        """
        Executes the nutrition search using the provided search term.

        :param self: This instance of the CommandLineHandler class.
        :param search_term: The term to search for in the nutrition repository.
        :type search_term: str
        :return: The selected product, cancel command, or None.
        :rtype: Nutrition | str | None
        """

        with terminal.console.status("Searching...", spinner="earth"):
            search_results = retriever_manager.get(configuration).retrieve(
                search_term, top_k=9
            )

            try:
                products = self.__resolve_results(search_results)
            except (ValueError, LookupError) as error:
                log.error("Cannot resolve nutrition search results: %s", error)
                terminal.print_info(f"Cannot display nutrition search results: {error}")
                return None

        product_count = len(products)

        if product_count == 0:
            terminal.print_info(
                f"No products found for search term: '[yellow]{search_term}[/yellow]'"
            )
        else:
            terminal.print_rule_separated(
                f"{product_count} products for search term: '{search_term}'"
            )

            choices = []
            self._add_navigation_choices_to_menu(choices)
            self._add_item_choices_to_menu(choices, products)

            return terminal.safe_select(
                "Select a product to view details:",
                choices=choices,
            )

    def __resolve_results(self, results: list[DocumentResult]) -> list[Nutrition]:
        """
        Loads the nutrition records referenced by search results in ranked order.

        :param results: Ranked sqlite-rag search results.
        :type results: list[DocumentResult]
        :return: Nutrition records in the same order as the search results.
        :rtype: list[Nutrition]
        :raises ValueError: If a result has invalid nutrition metadata.
        :raises LookupError: If a referenced nutrition record is missing.
        """
        ids = []

        for result in results:
            metadata = result.document.metadata

            if not isinstance(metadata, dict):
                raise ValueError("A search result has invalid nutrition metadata.")
            
            nutrition_id = metadata.get("nutrition_id")

            if (
                metadata.get("entity_type") != "nutrition"
                or type(nutrition_id) is not int
                or nutrition_id <= 0
            ):
                raise ValueError("A search result has invalid nutrition metadata.")
            
            ids.append(nutrition_id)

        if not ids:
            return []

        with database_engine.get_db() as session:
            records = NutritionRepository(session).get_by_ids(ids)

        missing = set(ids) - records.keys()

        if missing:
            raise LookupError(
                f"Search results refer to {len(missing)} missing nutrition record(s). "
                "Update the embeddings before searching again."
            )
        
        return [records[nutrition_id] for nutrition_id in ids]

    def _add_navigation_choices_to_menu(self, choices) -> None:
        """
        Adds the cancel choice to the list of choices.

        :param choices: The current list of choices.
        :type choices: list[questionary.Choice]
        """

        choices += [
            questionary.Choice(
                title=[
                    (
                        "bold fg:ansired ",
                        "Cancel",
                    ),
                ],
                value=self.CANCEL_COMMAND,
                shortcut_key=str(0),  # Assign shortcut key '0' to Cancel
            ),
        ]

    def _add_item_choices_to_menu(self, choices, products):
        """
        Adds product item choices to the list of choices.

        :param choices: The current list of choices.
        :param products: The products search results.
        """

        for index, product in enumerate(products, start=1):
            brands = ", ".join(product.brands or [])
            choices.append(
                questionary.Choice(
                    title=[
                        (
                            "bold fg:ansiyellow ",
                            f"{brands} {product.name or ''} {product.quantity or ''}".strip(),
                        ),
                        (
                            "fg:ansibrightblack ",
                            f" | {product.energy_100g_kj} kJ | {product.carbohydrates_100g} g carbs | {product.proteins_100g} g proteins | {product.fat_100g} g fat | {product.sugars_100g} g sugars | {product.salt_100g} g salt",
                        ),
                    ],
                    value=product,
                    shortcut_key=str(index) if index < 10 else None,
                )
            )

    def _print_nutrition_info(self, product: Nutrition):
        """
        Prints the nutritional information of the product in a table format.

        :param self: This instance of the CommandLineHandler class.
        :param product: The product details.
        :type product: Nutrition
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

        title = (
            f"{', '.join(product.brands or [])} "
            f"{product.name or ''} {product.quantity or ''}"
        ).strip()
        if product.url:
            title = f"[link={product.url}]{title}[/link]"
        terminal.print_rule_separated(title)
        nutrients = {}
        for field in fields(product):
            if field.name.endswith("_100g") or field.name == "energy_100g_kj":
                value = getattr(product, field.name)
                if value is not None:
                    name = field.name.replace("_100g_kj", "").replace("_100g", "")
                    unit = "kJ" if field.name == "energy_100g_kj" else "g"
                    nutrients[name.replace("_", " ").title()] = f"{value} {unit}"
        _print_nutrition_table(nutrients, "Nutrient", "Amount per 100g")
