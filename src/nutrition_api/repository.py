import openfoodfacts
import config.config as conf


class NutritionRepository:
    def __init__(self):
        """
        Initializes the repository by setting up the Open Food Facts API client.
        Attributes:
            api (openfoodfacts.API): An instance of the Open Food Facts API client configured
            with the application name, version, and environment.
        """

        self.api = openfoodfacts.API(
            user_agent=f"{conf.app_name}/{conf.version}",
            version=openfoodfacts.APIVersion.v3,
            environment=openfoodfacts.Environment.org,
            country=openfoodfacts.Country.de,
            timeout=30,
        )

    def search_foods(self, query: str, page: int = 1, page_size: int = 20):
        """
        Searches for food products based on a query string.
        Args:
            query (str): The search term to find food products.
            page_size (int, optional): The number of results to return. Defaults to 10.
        Returns:
            list: A list of food products matching the search query.
        """

        return self.api.product.text_search(query, page=page, page_size=page_size)
