import logging
import questionary

from persons.person import Gender, Person
from rich.table import Table
from common.terminal import terminal
from typing import Any
from persistence.unit_of_work import UnitOfWork

log = logging.getLogger(__name__)


class CommandLineHandler:
    """CommandLineHandler class for managing the command line interface related to persons."""

    CANCEL_COMMAND = "CANCEL"
    ADD_PERSON_COMMAND = "ADD_PERSON"
    DELETE_PERSON_COMMAND = "DELETE_PERSON"
    VIEW_PERSONS_COMMAND = "VIEW_PERSONS"

    def __init__(self):
        """
        Initializes the CommandLineHandler.

        :param self: This instance of the CommandLineHandler class.
        """
        with UnitOfWork() as uow:
            self._activity_levels = uow.activity_levels.get_all()

    def show(self):
        """
        Displays the command line interface to the user and handles input.

        :param self: This instance of the CommandLineHandler class.
        """
        while True:
            command = self._get_menu_selection()

            if command is None or command == self.CANCEL_COMMAND:
                return  # User chose to cancel; return to main menu.

            if command == self.VIEW_PERSONS_COMMAND:
                self._view_persons()

            if command == self.ADD_PERSON_COMMAND:
                self._add_person()

            if command == self.DELETE_PERSON_COMMAND:
                self._delete_person()

    def _get_menu_selection(self) -> Any:
        """
        Displays the menu and gets the user's selection.

        :param self: This instance of the CommandLineHandler class.

        :return: The command selected by the user.
        :rtype: Any
        """

        choices = [
            questionary.Choice("View persons", value=self.VIEW_PERSONS_COMMAND),
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

        def _ask_personal_information() -> dict[str, Any]:
            """
            Asks the user to enter personal information for a new person.
            """
            return questionary.form(
                name=questionary.text(
                    "Enter the person's name: ",
                    validate=lambda text: 1 <= len(text) <= 100
                    or "The name must be between 1 and 100 characters long.",
                ),
                gender=questionary.select(
                    "Enter a biological gender: ", choices=[g.value for g in Gender]
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
                        questionary.Choice(al.name, value=al.id)
                        for al in self._activity_levels
                    ],
                ),
            ).ask()

        def _create_person() -> Person:
            """
            Creates a new Person instance and fills it with the provided information.

            :return: A new Person instance with the provided information.
            :rtype: Person
            """
            selected_activity_level_id = int(answers["activity_level"])

            selected_activity_level = next(
                (
                    activity_level
                    for activity_level in self._activity_levels
                    if activity_level.id == selected_activity_level_id
                ),
                None,
            )

            return Person(
                name=answers["name"],
                gender=answers["gender"],
                weight=float(answers["weight"]),
                height=float(answers["height"]),
                birth_year=int(answers["birth_year"]),
                activity_level=selected_activity_level,
            )

        def _try_add_person_to_repository(person: Person) -> bool:
            """
            Tries to add the person to the repository. If a person with the same name
            already exists, prompts the user to enter a different name or cancel the operation.

            :param person: The Person instance to be added to the repository.
            :type person: Person
            :return: True if the person was successfully added, False if the operation was cancelled.
            :rtype: bool
            """
            while True:
                with UnitOfWork() as uow:
                    if uow.persons.try_add(person):
                        uow.commit()
                        return True

                log.warning(f"A person with the name '{person.name}' already exists.")

                if questionary.confirm(
                    "Do you want to try a different name? If not the operation will be cancelled and all entered information will be lost."
                ).ask():
                    person.name = questionary.text(
                        "Enter the person's name: ",
                        validate=lambda text: text != "" or "Name cannot be empty.",
                    ).ask()
                else:
                    return False

        answers = _ask_personal_information()

        if not answers:
            log.info(f"Not all information was provided.")
            return

        person = _create_person()

        if not _try_add_person_to_repository(person):
            return

        terminal.print_dict_as_table(
            {
                "Name": person.name,
                "Gender": person.gender.value,
                "Weight (kg)": f"{person.weight:.0f}",
                "Height (cm)": f"{person.height:.0f}",
                "Birth Year": f"{person.birth_year}",
                "Activity Level": (
                    person.activity_level.name if person.activity_level else "None"
                ),
                "Needed Calories (kcal)": f"{person.calories_needed():.0f}",
            },
            column1_title="Attribute",
            column2_title="Value",
        )

    def _delete_person(self):
        """
        Deletes a person from the repository.

        :param self: This instance of the CommandLineHandler class.
        """

        def _select_person_to_delete() -> Any:
            """
            Prompts the user to select a person to delete from the repository.

            :return: The name of the person selected for deletion.
            :rtype: Any
            """
            with UnitOfWork() as uow:
                persons = uow.persons.get_all()

            if not persons:
                terminal.print_info("No persons available to delete.")
                return

            return questionary.autocomplete(
                "Select the person you want to delete:",
                choices=[person.name for person in persons],
                ignore_case=True,
                validate=lambda text: text
                in [person.name for person in persons]  # Only existing names are valid
                or "Please select an existing person to delete.",
            ).ask()

        person_name = _select_person_to_delete()

        if person_name:
            if questionary.confirm(
                f"Are you sure you want to delete the person '{person_name}'?"
            ).ask():
                with UnitOfWork() as uow:
                    uow.persons.delete(person_name)
                    uow.commit()

                terminal.print_info(f"Person '{person_name}' has been deleted.")

    def _view_persons(self):
        """
        Displays all persons in the repository.

        :param self: This instance of the CommandLineHandler class.
        """
        with UnitOfWork() as uow:
            persons = uow.persons.get_all()

        if not persons:
            terminal.print_info("No persons available to display.")
            return

        table = Table()
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Gender")
        table.add_column("Age", justify="right")
        table.add_column("Weight (kg)", justify="right")
        table.add_column("Height (cm)", justify="right")
        table.add_column("Activity Level")
        table.add_column("Needed Calories (kcal)", justify="right")

        for person in persons:
            table.add_row(
                person.name,
                person.gender.value,
                str(person.age()),
                f"{person.weight:.0f}",
                f"{person.height:.0f}",
                person.activity_level.name if person.activity_level else "None",
                f"{person.calories_needed():.0f}",
            )

        terminal.print(table)
