class InputHandler:
    EXIT_COMMAND = "EXIT"

    def handle_input(self):
        """
        Handles all user input.

        :param self: The reference to the current instance of the InputHandler class.
        :return: The command entered by the user.
        """
        input_value = input()

        if self._is_exit_command(input_value):
            return self.EXIT_COMMAND

    def _is_exit_command(self, input_value):
        """
        Checks if the given input value is the exit command.

        :param self: The reference to the current instance of the InputHandler class.
        :param input_value: The input value to check.
        """
        if input_value.lower().strip() == "exit":
            return True
