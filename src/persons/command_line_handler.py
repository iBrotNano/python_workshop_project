import logging
from persons.repository import Repository
import questionary
from persons.person import Person
from common.console import print_dict_as_table, print_info

log = logging.getLogger(__name__)


class CommandLineHandler:
    CANCEL_COMMAND = "CANCEL"
    ADD_PERSON_COMMAND = "ADD_PERSON"
    DELETE_PERSON_COMMAND = "DELETE_PERSON"

    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        """
        self.repository = Repository()

    def show(self):
        """
        Displays the command line interface to the user and handles input.
        """
        while True:
            command = self._get_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return  # User chose to cancel; return to main menu.

            if command == self.ADD_PERSON_COMMAND:
                self._add_person()

            if command == self.DELETE_PERSON_COMMAND:
                self._delete_person()

    def _get_menu_selection(self):
        """
        Displays the menu and gets the user's selection.

        :param self: This instance of the CommandLineHandler class.

        :return: The command selected by the user.
        """

        choices = [
            questionary.Choice(
                "Add a new person",
                value=self.ADD_PERSON_COMMAND,
            ),
            questionary.Choice("Delete a person", value=self.DELETE_PERSON_COMMAND),
            questionary.Choice(
                "Back to main menu",
                value=self.CANCEL_COMMAND,
            ),
        ]

        return questionary.select(
            "What do you want to do?", choices=choices, use_shortcuts=True
        ).ask()

    def _add_person(self):
        """
        Adds a new person to the repository.

        :param self: This instance of the CommandLineHandler class.
        """

        def _ask_personal_information():
            """
            Asks the user to enter personal information for a new person.
            """
            return questionary.form(
                name=questionary.text(
                    "Enter the person's name: ",
                    validate=lambda text: text != "" or "Name cannot be empty.",
                ),
                gender=questionary.select(
                    "Enter a biological gender: ", choices=Person.GENDERS
                ),
                weight=questionary.text(
                    "Enter your weight (in kg): ",
                    validate=lambda text: text.isdigit()
                    or "Please enter a valid number.",
                ),
                height=questionary.text(
                    "Enter your height (in cm): ",
                    validate=lambda text: text.isdigit()
                    or "Please enter a valid number.",
                ),
                birth_year=questionary.text(
                    "Enter your birth year: ",
                    validate=lambda text: text.isdigit()
                    or "Please enter a valid year.",
                ),
                activity_level=questionary.select(
                    "What is your activity level?",
                    choices=[
                        questionary.Choice(v[0], value=k)
                        for k, v in Person.ACTIVITY_LEVELS.items()
                    ],
                ),
            ).ask()

        def _create_person():
            """
            Creates a new Person instance and fills it with the provided information.
            """
            person = Person()
            person.name = answers["name"]
            person.gender = answers["gender"]
            person.weight = float(answers["weight"])
            person.height = float(answers["height"])
            person.birth_year = int(answers["birth_year"])
            person.activity_level = answers["activity_level"]
            return person

        def _try_add_person_to_repository(person: Person):
            """
            Tries to add the person to the repository. If a person with the same name
            already exists, prompts the user to enter a different name or cancel the operation.
            """
            while not self.repository.try_add(person):
                log.warning(f"A person with the name '{person.name}' already exists.")

                if questionary.confirm(
                    "Do you want to try a different name? If not the operation will be cancelled and all entered information will be lost."
                ).ask():
                    person.name = questionary.text(
                        "Enter the person's name: ",
                        validate=lambda text: text != "" or "Name cannot be empty.",
                    ).ask()
                else:
                    return

        answers = _ask_personal_information()

        if not answers:
            log.info(f"Not all information was provided.")
            return

        person = _create_person()
        _try_add_person_to_repository(person)

        print_dict_as_table(
            {
                "Name": person.name,
                "Gender": person.gender,
                "Weight (kg)": f"{person.weight:.0f}",
                "Height (cm)": f"{person.height:.0f}",
                "Birth Year": f"{person.birth_year}",
                "Activity Level": Person.ACTIVITY_LEVELS[person.activity_level][0],
                "Needed Calories (kcal)": f"{person.calculate_calories_needed():.0f}",
            },
            column1_title="Attribute",
            column2_title="Value",
        )

    def _delete_person(self):
        """
        Deletes a person from the repository.

        :param self: This instance of the CommandLineHandler class.
        """

        def _select_person_to_delete():
            """
            Prompts the user to select a person to delete from the repository.

            :return: The name of the person selected for deletion.
            """
            if not self.repository.data:
                print_info("No persons available to delete.")
                return

            return questionary.autocomplete(
                "Select the person you want to delete:",
                choices=list(self.repository.data.keys()),
                ignore_case=True,
                validate=lambda text: text
                in self.repository.data.keys()  # Only exiting names are valid
                or "Please select an existing person to delete.",
            ).ask()

        person_name = _select_person_to_delete()

        if person_name:
            if questionary.confirm(
                f"Are you sure you want to delete the person '{person_name}'?"
            ).ask():
                self.repository.delete(person_name)
                print_info(f"Person '{person_name}' has been deleted.")
