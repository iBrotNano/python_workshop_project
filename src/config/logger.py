import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config.config as conf


# Configure the logging system.
def configure():
    """
    Configure the application logger with both file and console handlers.
    Sets up a rotating file handler that writes logs.Additionally, configures console
    output via a StreamHandler.
    Log format includes timestamp, log level, and message.
    The logs directory is created automatically if it doesn't exist.
    Returns:
        None
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(conf.logging_folder)
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / conf.logging_file_name

    handler = RotatingFileHandler(
        log_file,
        maxBytes=conf.logging_file_size,
        backupCount=conf.logging_backup_count,
        encoding=conf.logging_encoding,
    )

    logging.basicConfig(
        level=conf.logging_basic_level,
        format=conf.logging_basic_format,
        handlers=[
            handler,
            logging.StreamHandler(),  # Console output
        ],
    )
