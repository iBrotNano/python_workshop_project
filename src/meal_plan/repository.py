from meal_plan.meal_plan import MealPlan
from meal_plan.meal_entity import MealEntity
from meal_plan.meal import Meal
from sqlalchemy.orm import Session
from meal_plan.meal_plan_entity import MealPlanEntity
from recipes.recipe_entity import RecipeEntity
from recipes.recipe import Recipe
from persons.person_entity import PersonEntity
from persons.person import Person


class Repository:
    """Repository class that holds the meal plan."""

    def __init__(self, session: Session):
        """
        Initializes the Repository with the provided SQLAlchemy session.

        :param session: The SQLAlchemy session instance.
        :type session: Session
        """
        self._session = session

    def _entity_to_model(self, entity: MealPlanEntity) -> MealPlan:
        meal_plan = MealPlan()

        for index, meal_entity in enumerate(entity.meals):
            recipe = None

            if meal_entity.recipe:
                recipe_data = {
                    key: value
                    for key, value in meal_entity.recipe.__dict__.items()
                    if key in Recipe.__dataclass_fields__
                }

                recipe = Recipe(**recipe_data)

            persons = []

            if meal_entity.persons:
                for person_entity in meal_entity.persons:
                    person_data = {
                        key: value
                        for key, value in person_entity.__dict__.items()
                        if key in Person.__dataclass_fields__
                    }

                    persons.append(Person(**person_data))

            meal = Meal(recipe=recipe, persons=persons if persons else None)
            day = index // 5
            meal_time = index % 5
            meal_plan._plan[day][meal_time] = meal

        return meal_plan

    def _model_to_entity(self, model: MealPlan) -> MealPlanEntity:
        flattend_plan = [meal for day in model.plan for meal in day]
        meal_entities = []

        for meal in flattend_plan:
            meal_entity = MealEntity()

            if meal is not None:
                if meal.recipe:
                    recipe_entity = (
                        self._session.query(RecipeEntity)
                        .filter_by(name=meal.recipe.name)
                        .first()
                    )

                    if recipe_entity:
                        meal_entity.recipe = recipe_entity

                if meal.persons:
                    person_entities = (
                        self._session.query(PersonEntity)
                        .filter(
                            PersonEntity.name.in_(
                                [person.name for person in meal.persons]
                            )
                        )
                        .all()
                    )

                    meal_entity.persons = person_entities

            meal_entities.append(meal_entity)

        return MealPlanEntity(meals=meal_entities)

    def create(self, meal_plan: MealPlan):
        """
        Creates a new meal plan in the repository.

        :param self: This instance of the Repository class.
        :param meal_plan: The meal plan to create.
        :type meal_plan: MealPlan
        """
        self.delete()  # TODO: Implement an update instead.
        entity = self._model_to_entity(meal_plan)
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._entity_to_model(entity)

    def get(self) -> MealPlan | None:
        """
        Gets a meal plan.

        :param self: This instance of the Repository class.
        :return: The meal plan if found, otherwise None.
        :rtype: MealPlan | None
        """
        entity = self._session.query(MealPlanEntity).first()

        if not entity:
            return None

        return self._entity_to_model(entity)

    def delete(self):
        """
        Deletes the meal plan from the repository.

        :param self: This instance of the Repository class.
        """
        entity = self._session.query(MealPlanEntity).first()

        if not entity:
            return

        self._session.delete(entity)
        self._session.commit()
