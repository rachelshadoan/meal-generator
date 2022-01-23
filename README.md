# meal-generator
A simple meal idea generator for people who know how to cook but don't know what to eat

## Requirements

[Git](https://git-scm.com/) and [Python3](https://www.python.org/download/releases/3.0/)

## How To Use

To use this generator, first clone the repo with the command

```git clone git@github.com:rachelshadoan/meal-generator.git```

Edit `ingredients.yaml` to reflect what is in your fridge and pantry. An ingredient entry looks like:
```
    <ingredient name>:
        category: <category name>
```

Current categories are `carbs`, `protein`, `liquids`, `veg`, `fruit`, but you can add any that you like.

Once you have `ingredients.yaml` reflecting what's available in your house, run the generator from your terminal with the command:

```python3 meal_generator.py```

That will produce a list of meal ideas from the meals defined in the `meals` directory. Run it as many times as you like,
you'll get different suggestions every time!