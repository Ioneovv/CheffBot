import json

def transform_recipe(recipe):
    """Преобразует рецепт в нужный формат."""
    # Преобразуем ингредиенты в нужный формат
    ingredients = []
    for item in recipe.get("ingredients", []):
        ingredients.append({
            "ingredient": item["ingredient"],
            "amount": item["amount"]
        })

    # Формируем новый рецепт
    return {
        "title": recipe["title"],
        "ingredients": ingredients,
        "instructions": recipe.get("instructions", []),
        "category": recipe.get("category", "")
    }

def transform_recipes(input_file, output_file):
    """Читает рецепты из input_file и записывает преобразованные в output_file."""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            recipes = json.load(file)

        transformed_recipes = [transform_recipe(recipe) for recipe in recipes]

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(transformed_recipes, file, ensure_ascii=False, indent=4)

        print(f"Файл {output_file} успешно создан!")

    except Exception as e:
        print(f"Ошибка: {e}")

# Пример использования
input_file1 = "recipes.json"  # Входной файл
output_file1 = "recipes_part1.json"  # Выходной файл
transform_recipes(input_file1, output_file1)
