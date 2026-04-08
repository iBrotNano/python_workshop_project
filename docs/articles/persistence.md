# Datamodel And Persistence

| Name   | Value      |
| :----- | :--------- |
| Status | ~Published |
| Owner  | @iBrotNano |

## Motivation

Developers who want to know about the data model of the app will find the needed information here.

## Datamodel

The app stores persons, recipes, meals and meal plans. Persons are persons in a household and used to calculate the needed nutrition. Recipes are containers for food and are used in meal plans to calculate the nutrition for meals. A meal plan ist a collection for meals for a household.

```mermaid
erDiagram
    activity_levels {
        integer id PK
        varchar name
        float multiplier
    }
    meal_person_association {
        integer meal_id FK, PK
        integer person_id FK, PK
    }
    meal_plans {
        integer id PK
    }
    meals {
        integer id PK
        integer slot_index
        integer meal_plan_id FK
        integer recipe_id FK
    }
    persons {
        integer id PK
        varchar name
        varchar gender
        float weight
        float height
        integer birth_year
        integer activity_level_id FK
    }
    recipes {
        integer id PK
        varchar name
        json ingredients
        text instructions
        json nutrition
        varchar type
    }
    meals ||--o{ meal_person_association : meal_id
    persons ||--o{ meal_person_association : person_id
    meal_plans ||..o{ meals : meal_plan_id
    recipes ||..o{ meals : recipe_id
    activity_levels ||..o{ persons : activity_level_id
```

## Adding new entities

If you need to add a new entity class to store data into the database it must be registered to ensure they are known by sqlalchemy. It can be registered in `persistence/model_registry.py`.

```py
def load_model_definitions():
    """
    Imports ORM model modules so SQLAlchemy metadata knows all table mappings.

    :raises ModuleNotFoundError: If a model module cannot be imported.
    """
    import_module("persistence.schema")
    import_module("meal_plan.meal_plan_entity")
    import_module("meal_plan.meal_entity")
	...
```

## Unity Of Work

All data access logic is encapsulated in a `unit_of_work.py`. It initializes the database session and all repositories. It handles commits, rollbacks when failures happens and frees resources like the session.

It can be used with `with`.

```py
with UnitOfWork() as uow:
    self._meal_plan = uow.meal_plans.get() or MealPlan()
```