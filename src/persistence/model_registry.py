from importlib import import_module


def load_model_definitions():
    """
    Imports ORM model modules so SQLAlchemy metadata knows all table mappings.

    :raises ModuleNotFoundError: If a model module cannot be imported.
    """
    import_module("persons.person_entity")
    import_module("recipes.recipe_entity")
