import openfoodfacts

from typing import Any


class Repository:
    """Repository class for handling interactions with the Open Food Facts API."""

    def __init__(self, api_client: openfoodfacts.API):
        """
        Initializes the repository by setting up the Open Food Facts API client.

        :param self: The instance of the Repository class.
        :param api_client: An instance of the Open Food Facts API client to be used for
        :type api_client: openfoodfacts.API
        """

        self._api_client = api_client

    def search_products(
        self, query: str, page: int = 1, page_size: int = 5
    ) -> dict[str, Any]:
        """
        Searches for food products based on a query string.

        :param self: The instance of the Repository class.
        :param query: The search term to find food products.
        :type query: str
        :param page: The page number for paginated results. Defaults to 1.
        :type page: int
        :param page_size: The number of results to return. Defaults to 10.
        :type page_size: int
        :return: A dictionary containing the search query, pagination info, and a flat list of food products matching the search query in a normalized format.
        :rtype: dict[str, Any]
        """

        search_result = self._api_client.product.text_search(
            query, page=page, page_size=page_size
        )

        # Build the result dictionary with pagination info.
        # Sometimes the API returns these values as strings, so we convert them to integers.
        result: dict[str, Any] = {
            "query": query,
            "count": int(search_result.get("count", 0)),
            "page": int(search_result.get("page", 1)),
            "page_count": int(search_result.get("page_count", 0)),
            "page_size": int(search_result.get("page_size", 0)),
            "skip": int(search_result.get("skip", 0)),
        }

        products: list[dict[str, Any]] = []

        # Extract product information, handling missing keys gracefully.
        # Makes a flat list, containing also relevant nutriments with 'N/A' as default value.
        for product in search_result["products"]:
            product_data = {
                "id": product.get("id", "N/A"),
                "url": product.get("url", "N/A"),
                "product": product.get("product_name", "N/A"),
                "brands": product.get("brands", "N/A"),
                "quantity": product.get("quantity", "N/A"),
                "energy-kcal_100g": product.get("energy-kcal_100g", "N/A"),
                "energy-kj_100g": product.get("energy-kj_100g", "N/A"),
                "carbohydrates_100g": product.get("carbohydrates_100g", "N/A"),
                "proteins_100g": product.get("proteins_100g", "N/A"),
                "fat_100g": product.get("fat_100g", "N/A"),
                "sugars_100g": product.get("sugars_100g", "N/A"),
                "salt_100g": product.get("salt_100g", "N/A"),
            }

            # Include all other nutriments available in the product data and overrides missing defaults.
            for key in product["nutriments"].keys():
                product_data[key] = product["nutriments"].get(key, "N/A")

            products.append(product_data)

        result["products"] = products
        return result
