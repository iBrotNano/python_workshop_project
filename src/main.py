import keyboard

# import nutrition_api.repository as nutrition_repo

# Encapsulates the whole application logic and displays any errors encountered.
try:
    # nutritionRepo = nutrition_repo.NutritionRepository()
    # nutritionRepo.search("apple")
    print("Type Ctrl+C to exit.")

    while True:
        if keyboard.is_pressed("ctrl+c"):
            print("Exiting the application.")
            break
except Exception as e:
    print(f"An error of type {type(e)} occurred. Message: {e}")
