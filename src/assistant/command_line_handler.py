import logging

from typing import Any
from common.terminal.terminal import terminal
from config.configuration import configuration
from assistant.prompt import Prompt
from rich.markdown import Markdown

log = logging.getLogger(__name__)


class CommandLineHandler:
    """Handles the command line interface for nutrition-related features."""

    QUESTION_COMMAND = "QUESTION"
    CANCEL_COMMAND = "CANCEL"

    def show(self):
        """
        Displays the command line interface to the user and handles input.

        :param self: This instance of the CommandLineHandler class.
        """

        command, question = self._get_question()

        if command == self.CANCEL_COMMAND:
            return  # User chose to cancel; return to main menu.

        if command == self.QUESTION_COMMAND and question is not None:
            result = self._prompt(question)

            if result is None or result == self.CANCEL_COMMAND:
                return  # User chose to cancel during search; return to main menu.

    def _get_question(self) -> tuple[str, str | None]:
        """
        Prompts the user to enter a question about nutritional information.

        :param self: This instance of the CommandLineHandler class.

        :return: The search term entered by the user with the search nutrition command or a cancel command if none is entered or CTRL+C is pressed.
        :rtype: tuple[str, str | None]
        """

        question = terminal.safe_text("How can I help you?")

        if question is None or type(question) is not str or question.strip() == "":
            terminal.print_info("Nothing asked.")
            return (self.CANCEL_COMMAND, None)

        return (self.QUESTION_COMMAND, question.strip())

    def _prompt(self, query: str) -> dict | str | None:
        """
        Executes the nutrition chat using the provided query and keeps the conversation open.

        :param self: This instance of the CommandLineHandler class.
        :param query: The term to search for in the nutrition repository.
        :type search_term: str
        :return: The selected product, next/previous command, or cancel command.
        :rtype: dict | str | None
        """

        messages: list[dict[str, Any]] | None = None

        while True:
            prompt = Prompt(configuration)
            response, messages = prompt.execute(query, 9, messages)
            terminal.print(Markdown(response))
            command, next_query = self._get_question()

            if command == self.CANCEL_COMMAND:
                return self.CANCEL_COMMAND

            if next_query is not None:
                query = next_query
