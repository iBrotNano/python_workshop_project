import signal

from types import FrameType


class SigintHandler:
    """
    Handles SIGINT requests and restores the previous signal handler.
    """

    def __init__(self):
        """
        Initializes the SIGINT handler state.
        """
        self.__cancellation_requested = False
        self.__original_handler = None

    @property
    def is_cancellation_requested(self) -> bool:
        """
        Indicates whether cancellation was requested via Ctrl+C.

        :return: True if cancellation was requested, otherwise False.
        :rtype: bool
        """
        return self.__cancellation_requested

    def set(self):
        """
        Installs the temporary SIGINT handler.
        """
        self.__original_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.__request_cancellation)

    def unset(self):
        """
        Restores the original SIGINT handler.
        """
        if self.__original_handler is not None:
            signal.signal(signal.SIGINT, self.__original_handler)

    def __request_cancellation(self, _signal_number: int, _frame: FrameType | None):
        """
        Marks cancellation as requested when SIGINT is received.

        :param _signal_number: The received signal number.
        :type _signal_number: int
        :param _frame: The current stack frame.
        :type _frame: FrameType | None
        """
        self.__cancellation_requested = True

    def __enter__(self):
        """
        Installs the handler for use as a context manager.

        :return: The active SIGINT handler instance.
        :rtype: SigintHandler
        """
        self.set()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Restores the previous SIGINT handler when leaving the context.

        :param exc_type: The exception type if one occurred.
        :param exc_val: The exception value if one occurred.
        :param exc_tb: The traceback if one occurred.
        :return: False to propagate exceptions.
        :rtype: bool
        """
        self.unset()
        return False
