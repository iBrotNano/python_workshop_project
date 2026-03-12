import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.configuration import Configuration, configuration


# Configure the logging system.
class LoggerConfigurator:
    """Encapsulates the configuration of the logging system."""

    def __init__(self, configuration: Configuration):
        """
        Initializes the LoggerConfigurator with the given configuration.

        :param configuration: The Configuration instance containing logging settings.
        """
        self._configuration = configuration

    def configure(self):
        """
        Configure the application logger with both file and console handlers.
        Sets up a rotating file handler that writes logs.Additionally, configures console
        output via a StreamHandler.
        Log format includes timestamp, log level, and message.
        The logs directory is created automatically if it doesn't exist.
        """
        # Create logs directory if it doesn't exist
        log_dir = Path(self._configuration.logging_folder)
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / self._configuration.logging_file_name

        handler = RotatingFileHandler(
            log_file,
            maxBytes=self._configuration.logging_file_size,
            backupCount=self._configuration.logging_backup_count,
            encoding=self._configuration.logging_encoding,
        )

        logging.basicConfig(
            level=self._configuration.logging_basic_level,
            format=self._configuration.logging_basic_format,
            handlers=[
                handler,
                logging.StreamHandler(),  # Console output
            ],
        )


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
logger_configurator = LoggerConfigurator(configuration)
