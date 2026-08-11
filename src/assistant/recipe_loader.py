import json
import os
from difflib import get_close_matches

class RecipeLoader:
    def __init__(self, file_path="data/recipes.json"):
        self.file_path = file_path
        self.recipes = []
        self._load_recipes()

    def _load_recipes(self):
        """Метод загрузки файла с рецептами"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Критическая ошибка: файл {self.file_path} не найден.")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.recipes = data.get("recipes", [])
                if not self.recipes:
                    raise ValueError("Файл рецептов пуст или не содержит секции 'resipes'.")
                print(f"Успешно загружено {len(self.recipes)} рецептов.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Ошибка парсинга JSON в файле '{self.file_path}': {e.message}",
                e.doc,
                e.pos
            )

    def find_recipe(self, user_input: str):
        """Ищет рецепт по названию"""
        user_input = user_input.lower().strip()

        # Точный поиск: содержится ли название в запросе и наоборот
        for recipe in self.recipes:
            recipe_name = recipe.get("name", "").lower()
            if recipe_name in user_input or user_input in recipe_name:
                return recipe

        recipe_names = [r.get("name", "").lower() for r in self.recipes]

        # Находим самое похожее название (схожесть 60%, параметр cutoff)
        matches = get_close_matches(user_input, recipe_names, n=1, cutoff=0.6)
        if matches:
            matched_name = matches[0]
            for recipe in self.recipes:
                if recipe.get("name", "").lower() == matched_name:
                    return recipe

        return None

    def get_all_recipe_name(self):
        """Возвращает список всех названий"""
        return [r.get("name", "") for r in self.recipes]
