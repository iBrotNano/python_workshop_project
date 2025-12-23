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
            version=conf.openfoodfacts_api_version,
            environment=conf.openfoodfacts_api_environment,
            country=conf.openfoodfacts_api_country,
            timeout=conf.openfoodfacts_api_timeout,
        )

    def search_products(self, query: str, page: int = 1, page_size: int = 5):
        """
        Searches for food products based on a query string.
        Args:
            query (str): The search term to find food products.
            page (int, optional): The page number for paginated results. Defaults to 1.
            page_size (int, optional): The number of results to return. Defaults to 10.
        Returns:
            dict: A dictionary containing the search query, pagination info, and a flat list of food products matching the search query in a normalized format.
        """

        search_result = self.api.product.text_search(
            query, page=page, page_size=page_size
        )

        # Build the result dictionary with pagination info.
        result = {
            "query": query,
            "count": search_result.get("count", 0),
            "page": search_result.get("page", 1),
            "page_count": search_result.get("page_count", 0),
            "page_size": search_result.get("page_size", 0),
            "skip": search_result.get("skip", 0),
        }

        products = []

        # Extract product information, handling missing keys gracefully.
        # Makes a flat list, containing also relevant nutriments with 'N/A' as default value.
        for product in search_result["products"]:
            product_data = {
                "id": product.get("id", "N/A"),
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
