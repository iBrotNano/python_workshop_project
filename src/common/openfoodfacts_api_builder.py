import openfoodfacts

from config.configuration import Configuration, configuration


class OpenFoodFactsApiBuilder:
    """
    Configures the Open Food Facts API client with the necessary parameters.
    This class is responsible for setting up the API client using the configuration
    defined in the configuration module.
    """

    def __init__(self, configuration: Configuration):
        """
        Initializes the configurator with the provided configuration.

        :param configuration: An instance of the Configuration class containing API settings.
        """
        self._configuration = configuration

    def build(self) -> openfoodfacts.API:
        """
        Configures and returns an instance of the Open Food Facts API client.

        :param self: The instance of the OpenFoodFactsApiBuilder class.
        """

        return openfoodfacts.API(
            user_agent=f"{self._configuration.app_name}/{self._configuration.version}",
            version=self._configuration.openfoodfacts_api_version,
            environment=self._configuration.openfoodfacts_api_environment,
            country=self._configuration.openfoodfacts_api_country,
            timeout=self._configuration.openfoodfacts_api_timeout,
        )


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
openfoodfacts_api_builder = OpenFoodFactsApiBuilder(configuration)
api_client = openfoodfacts_api_builder.build()
