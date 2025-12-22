import logging
import input.input_handler as input_handler
import config.logger as logger_config

# import nutrition_api.repository as nutrition_repo

# Encapsulates the whole application logic and displays any errors encountered.
try:
    # nutritionRepo = nutrition_repo.NutritionRepository()
    # nutritionRepo.search("apple")
    logger_config.configure()  # First step in the app to make logging available everywhere.
    inputHandler = input_handler.InputHandler()
    log = logging.getLogger(__name__)

    print("Type 'exit' to exit the application.")

    while True:
        try:
            command = inputHandler.handle_input()

            if command == inputHandler.EXIT_COMMAND:
                print("Exiting the application.")
                break
        except Exception as e:
            log.exception(f"An error of type {type(e)} occurred. Message: {e}")

# Catch any unexpected errors at the top level during app initialization.
except Exception as e:
    log.critical(f"An error of type {type(e)} occurred. Message: {e}", exc_info=True)
