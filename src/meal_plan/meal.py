from recipes.recipe import Recipe


class Meal:
    def __init__(self):
        self.recipe = None
        self.nutrition_info = None

    def set_recipe(self, recipe: Recipe):
        self.recipe = recipe

    # TODO: Calculate nutrition info based on the recipe and the persons in the household.
