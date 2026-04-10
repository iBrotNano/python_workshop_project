import logging

from contextlib import contextmanager


@contextmanager
def suppress_console_logging():
    """
    Temporarily removes console log handlers while Rich progress is active.

    This keeps the progress rendering stable without affecting file logging.
    """
    root_logger = logging.getLogger()

    console_handlers = [
        handler
        for handler in root_logger.handlers
        if isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
    ]

    for handler in console_handlers:
        root_logger.removeHandler(handler)

    try:
        yield
    finally:
        for handler in console_handlers:
            root_logger.addHandler(handler)
