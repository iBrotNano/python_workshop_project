import logging
import sys
import input.input_handler as input_handler
import config.logger as logger_config
import nutrition_api.repository as nutrition_repository

# import nutrition_api.repository as nutrition_repo

# Encapsulates the whole application logic and displays any errors encountered.
try:
    # nutritionRepo = nutrition_repo.NutritionRepository()
    # nutritionRepo.search("apple")
    logger_config.configure()  # First step in the app to make logging available everywhere.
    inputHandler = input_handler.InputHandler()
    log = logging.getLogger(__name__)

    print("You can type 'exit' everywhere to exit the application.")

    while True:
        try:
            ### TEST CODE ###
            test = nutrition_repository.NutritionRepository().search_foods("Ja Skyr")
            # print(test)
            # test = test["products"][0]
            # print(type(test))
            # print(len(test))
            # print(test)

            for product in test["products"]:
                print(f"ID: {product.get('id', 'N/A')}")
                print(f"Product: {product.get('product_name', 'N/A')}")
                print(f"  Brands: {product.get('brands', 'N/A')}")
                print(f"  Quantity: {product.get('quantity', 'N/A')}")
                for key, value in product["nutriments"].items():
                    print(f"    {key}: {value}")
                print("")

            ### TEST CODE ###
            command = inputHandler.handle_input()

            if command == inputHandler.EXIT_COMMAND:
                print("Exiting the application.")
                sys.exit(0)

        except Exception as e:
            log.exception(f"An error of type {type(e)} occurred. Message: {e}")

# Catch any unexpected errors at the top level during app initialization.
except Exception as e:
    log.critical(f"An error of type {type(e)} occurred. Message: {e}", exc_info=True)
    sys.exit(1)  # Exit with error code 1 to indicate failure.
