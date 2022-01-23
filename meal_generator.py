from ast import Dict
from unicodedata import category
import yaml
import sys
import random
import collections
from dataclasses import dataclass, field
from typing import List
from typing import Dict

@dataclass
class Ingredient:
    category: str
    name: str

@dataclass
class Larder:
    categories: Dict = field(init=False)
    ingredients: Dict

    class FoodNotFoundException(Exception):
        pass

    class CategoryNotFoundException(Exception):
        pass

    def __post_init__(self):
        self.categories = {}

        for name in self.ingredients:
            ingredient = self.ingredients[name]
            if ingredient.category not in self.categories:
                self.categories[ingredient.category] = []
            self.categories[ingredient.category].append(ingredient)

    def get_by_name(self, name):
        if name in self.ingredients:
            return self.ingredients[name]
        raise Larder.FoodNotFoundException(name)

    def get_by_category(self, category):
        if category in self.categories:
            return self.categories[category]
        raise Larder.CategoryNotFoundException(category)
    
    def generate_food_combination(self, recipe_conf):
        food_bag = []

        for choice in recipe_conf["choices"]:
            food_bag += choice.choose(self)

        food_kinds = sorted([ food.name for food in food_bag if food.name not in recipe_conf["implicitly_named_ingredients"]])
        recipe_name = " ".join(food_kinds) + " " + recipe_conf["name"]

        return recipe_name


@dataclass
class ChooseOne:
    name: str

    def choose(self, larder):
        return [larder.get_by_name(self.name)]

@dataclass
class ChooseSome:
    category: str
    min: int
    max: int

    def __post_init__(self):
        self.min = int(self.min)
        self.max = int(self.max)

    def choose(self, larder):
        ingredients_in_category = larder.get_by_category(self.category)
        return [ random.choice(ingredients_in_category) for i in range(self.min, self.max) ]

def init_class(class_conf):
    class_type = next(iter(class_conf))
    class_params = class_conf[class_type]
    class_class = getattr(sys.modules[__name__], class_type)
    return class_class(**class_params)

def load_recipe_spec(path):
    with open(path, "r") as recipe_file:
        recipe_conf = yaml.load(recipe_file, Loader=yaml.BaseLoader)
        recipe_conf["choices"] = [ init_class(conf) for conf in recipe_conf["choices"] ]
        return recipe_conf
 
def load_larder():
    ingredients = {}
    with open("ingredients.yaml", "r") as ingredients_file:
        ingredients_dict = yaml.load(ingredients_file, Loader=yaml.BaseLoader)["ingredients"]
        for name in ingredients_dict:
            i = ingredients_dict[name]
            i["name"] = name
            ingredients[name] = Ingredient(**i)

    return Larder(ingredients)

def main():
    path = "meals/fried_rice.yaml"

    larder = load_larder()

    recipe_spec = load_recipe_spec(path)

    recipe_name = larder.generate_food_combination(recipe_spec)
    
    print(f"{recipe_name=}")

if __name__ == "__main__":
    main()