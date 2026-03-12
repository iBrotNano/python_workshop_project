import openfoodfacts

from config.configuration import Configuration, configuration


class OpenFoodFactsApiConfigurator:
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
        self._api_client = None

    @property
    def api_client(self) -> openfoodfacts.API | None:
        """
        Returns the configured Open Food Facts API client.

        :return: An instance of the Open Food Facts API client.
        :rtype: openfoodfacts.API
        """
        return self._api_client

    def configure(self):
        """
        Configures and returns an instance of the Open Food Facts API client.

        :param self: The instance of the OpenFoodFactsApiConfigurator class.
        """

        self._api_client = openfoodfacts.API(
            user_agent=f"{self._configuration.app_name}/{self._configuration.version}",
            version=self._configuration.openfoodfacts_api_version,
            environment=self._configuration.openfoodfacts_api_environment,
            country=self._configuration.openfoodfacts_api_country,
            timeout=self._configuration.openfoodfacts_api_timeout,
        )


openfoodfacts_api_configurator = OpenFoodFactsApiConfigurator(configuration)
