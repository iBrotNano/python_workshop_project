from config.logger_configurator import logger_configurator


class Configurator:
    """Encapsulates the configuration of the app."""

    def configure(self):
        """
        Configures the app by setting up logging and the OpenFoodFacts API.

        :param self: The instance of the Configurator class.
        """
        logger_configurator.configure()


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configurator = Configurator()
