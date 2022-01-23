from ast import Dict
from unicodedata import category
import yaml
import sys
import random
import collections
from dataclasses import dataclass, field
from typing import List
from typing import Dict
from os import listdir
from os.path import isfile, join

@dataclass(frozen=True)
class Ingredient:
    category: str
    name: str

def stem(food_name):
    if food_name.endswith("es"):
        return food_name[:-2]
    if food_name.endswith("s"):
        return food_name[:-1]

    return food_name

def capitalize(food_name):
    name_parts = []
    for name_part in food_name.split(" "):
        name_parts.append(name_part.capitalize())
    
    return  " ".join(name_parts)

def pretty_print_recipe(food_bag, recipe_conf):

    food_kinds = sorted([ capitalize(stem(food.name)) for food in food_bag if food.name not in recipe_conf["implicitly_named_ingredients"]])
    recipe_name = (" ".join(food_kinds) + " " + recipe_conf["name"]).replace("Canned ", "")

    full_recipe = recipe_name + "\n\t-" + "\n\t-".join([food.name for food in food_bag])

    return full_recipe

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
        food_bag = set()

        for choice in recipe_conf["choices"]:
            for ingredient in choice.choose(self):
                food_bag.add(ingredient)

        return pretty_print_recipe(food_bag, recipe_conf)


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
        top_range = random.randint(self.min, self.max)
        return [ random.choice(ingredients_in_category) for i in range(0, top_range) ]

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

    recipe_specs = []
    recipe_dir = "meals/"
    recipe_paths = []

    for f in listdir(recipe_dir):
        file_path = join(recipe_dir, f)
        if(isfile(file_path)):
            recipe_paths.append(file_path)

    random.shuffle(recipe_paths)

    for path in recipe_paths:
        recipe_specs.append(load_recipe_spec(path))

    larder = load_larder()

    for spec in recipe_specs:

        recipe = larder.generate_food_combination(spec)
        print(f"{recipe}") 

                
    

if __name__ == "__main__":
    main()