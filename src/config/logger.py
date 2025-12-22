import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Configure the logging system.
def configure():
    """
    Configure the application logger with both file and console handlers.
    Sets up a rotating file handler that writes logs to 'logs/app.log' with a maximum
    file size of 1 MB and keeps up to 5 backup files. Additionally, configures console
    output via a StreamHandler.
    Log format includes timestamp, log level, and message.
    The logs directory is created automatically if it doesn't exist.
    Returns:
        None
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1 MB
        backupCount=5,
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            handler,
            logging.StreamHandler(),  # Console output
        ],
    )
