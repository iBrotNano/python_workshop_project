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

## Database maintenance

After creating and quantizing embeddings, open **Settings → Database** and select
**Compact the database** when you want to reclaim space. Compaction is optional
and is never run automatically. The prompt shows the database size and bytes on
completely free pages; even with no free pages, partially filled pages may be
repacked, so this number is not an exact prediction of the savings.

Back up the database and close other application instances and tools before
compacting. SQLite needs exclusive access and may require up to twice the
database size in additional disk space. The command creates a compacted copy
beside the original and verifies sentence row IDs before replacing it, because
the vector index refers to those IDs. If verification or compaction fails before
replacement, the original is left in place and the error is displayed. The command currently
requires SQLite's `DELETE` journal mode; it refuses databases in WAL mode.

Nutrition search reuses its retriever while the application is open and closes it
before an update, compaction, or shutdown. With sqlite-rag 0.1.4, sentence
highlights are calculated in a single vector scan for each group of search
results. Other sqlite-rag versions use the library's original search method.
Search time still depends on the number of vectors, storage, and available
memory; compaction alone is not a guarantee of faster searches.

Stored recipes can be indexed from **Settings → Database → Create embeddings for stored recipes**. Their embeddings are
kept in a separate `data_recipes.db` sidecar database so recipe indexing does
not modify the nutrition embeddings in `data.db`. Recipe documents use stable
recipe IDs; running the indexing action again skips documents that are already
present. Newly saved recipes are indexed automatically after their database
transaction commits. If embedding creation fails, the recipe remains saved and
the error is reported; use **Settings → Database → Create embeddings for stored recipes** to retry missing documents. Existing recipe embeddings
are not overwritten.

From **Settings → Database**, use **Remove orphaned recipe embeddings** to clean
up embeddings left by earlier deletions or changes made outside the application.
Application recipe deletions normally remove their embeddings automatically. If
cleanup fails, the recipe remains deleted and the application reports the
failure; run the cleanup action again to retry. Embeddings associated with an
existing recipe are preserved, including when a recipe ID has been reused.
Unrecognized recipe document URIs are reported and left untouched.

For performance comparisons, use a read-only database connection or a separate
copy. Initialize the embedding model once, then time repeated representative
queries including nutrition-record lookup, separately from first-use model
initialization and interactive selection. Record `top_k`, result counts, and
individual timings, and compare ranked results and sentence highlights with
the original search.