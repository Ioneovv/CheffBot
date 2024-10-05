import json

with open('recipes.json', 'r', encoding='utf-8') as file:
    recipes = json.load(file)
    print(recipes)
