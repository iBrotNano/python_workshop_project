from config.logger_configurator import logger_configurator
from config.llama_cpp_configurator import llama_cpp_configurator
from config.configuration import Configuration


class Configurator:
    """Encapsulates the configuration of the app."""

    def configure(self, configuration: Configuration):
        """
        Configures the app by setting up the app's configuration.

        :param self: The instance of the Configurator class.
        :param configuration: The configuration settings for the app.
        """
        logger_configurator.configure()
        llama_cpp_configurator.configure()


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
configurator = Configurator()
