import logging
import questionary
from meal_plan.repository import Repository
from common.console import print_info

log = logging.getLogger(__name__)


class CommandLineHandler:
    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        :param repository: The meal plan repository.
        :type repository: Repository
        """
        self.repository = Repository()

    def show(self):
        if not self.repository.meal_plan:
            print_info("No meal plan is present.")
            return
