import json

# Загрузка исходного файла
with open('recipes.json', 'r', encoding='utf-8') as file:
    recipes = json.load(file)

# Разделение списка рецептов на две части
half = len(recipes) // 2
recipes_part1 = recipes[:half]
recipes_part2 = recipes[half:]

# Сохранение первой части
with open('recipes_part1.json', 'w', encoding='utf-8') as file:
    json.dump(recipes_part1, file, ensure_ascii=False, indent=4)

# Сохранение второй части
with open('recipes_part2.json', 'w', encoding='utf-8') as file:
    json.dump(recipes_part2, file, ensure_ascii=False, indent=4)

print("Файлы успешно разбиты на recipes_part1.json и recipes_part2.json.")
