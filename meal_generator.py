from unicodedata import category
import yaml
import sys
import random
from dataclasses import dataclass
from typing import List

@dataclass
class Ingredient:
    category: str
    kind: str

@dataclass
class IngredientSpec:
    category: str
    kind: str = None
    limit: int = 1

    def matches(self, recipe):
        for ingredient in recipe:
            if self.matches_ingredient(ingredient):
                return True

        return False

    def matches_ingredient(self, ingredient):
        if self.category != ingredient.category:
            return False
        elif self.kind and ingredient.kind != self.kind:
            return False
        else:
            return True


@dataclass
class CompoundSpec:
    ingredient_specs: List
    operator: str

    def __post_init__(self):
        rehydrated_ingredients = []
        for conf in self.ingredient_specs:
            rehydrated_ingredients.append(make_constraint(conf))
        self.ingredient_specs = rehydrated_ingredients
        operator_function = getattr(sys.modules["builtins"], self.operator)
        self.operator = operator_function

    def matches(self, recipe):
        subclause_values = [ spec.matches(recipe) for spec in self.ingredient_specs ]
        return self.operator(subclause_values)

def make_constraint(constraint_conf):
    constraint_type = next(iter(constraint_conf))
    constraint_parameters = constraint_conf[constraint_type]
    constraint_class = getattr(sys.modules[__name__], constraint_type)
    return constraint_class(**constraint_parameters)

def load_recipe_spec(path):
    with open(path, "r") as recipe_file:
        recipe_conf = yaml.load(recipe_file, Loader=yaml.BaseLoader)
        recipe_conf["schema"] = make_constraint(recipe_conf["schema"])
        return recipe_conf
        

def generate_recipe(recipe_conf, max_attempts=100):
    ingredients_list = get_ingredient_options()

    for attempt in range(max_attempts):
        fridge = ingredients_list.copy()
        random.shuffle(fridge)
        food_bag = []
        while fridge:
            food_bag.append(fridge.pop())
            if recipe_conf["schema"].matches(food_bag):
                food_kinds = sorted([ food.kind for food in food_bag if food.kind not in recipe_conf["implicitly_named_ingredients"]])
                recipe_name = " ".join(food_kinds) + " " + recipe_conf["name"]
                return recipe_name
    return None



def get_ingredient_options():
    ingredient_options = []

    ingredient_options.append(Ingredient("veg", "pickles"))
    ingredient_options.append(Ingredient("protein", "ice cream"))
    ingredient_options.append(Ingredient("carb", "rice"))
    ingredient_options.append(Ingredient("carb", "bread"))
    ingredient_options.append(Ingredient("protein", "bacon"))
    ingredient_options.append(Ingredient("veg", "bok choi"))
    ingredient_options.append(Ingredient("veg", "scallions"))
    ingredient_options.append(Ingredient("protein", "cheddar cheese"))
    ingredient_options.append(Ingredient("protein", "egg"))
    ingredient_options.append(Ingredient("protein", "milk"))
    ingredient_options.append(Ingredient("carb", "elbow macaroni"))
    ingredient_options.append(Ingredient("carb", "yellow potatos"))

    return ingredient_options

def main():
    path = "meals/fried_rice.yaml"
    recipe_spec = load_recipe_spec(path)

    recipe = generate_recipe(recipe_spec)

    print(f"{recipe=}")

if __name__ == "__main__":
    main()