import re
import logging
from datasets import load_dataset
from src.database.db import get_connection_db

logger = logging.getLogger(__name__)

def load_recipes(limit: int | None = None):
    """Функция загрузки датасета"""
    split = f"train[:{limit}]" if limit else "train"
    return load_dataset("epishchik/RuRecipes-93k", split=split)

def parse_ingredients(ingredients: list[str]) -> list[dict]:
    """
    Функция парсинга ингредиентов.
    Достает из строки название, количество и единицу измерения ингредиента
    """
    parsed_ingredients = []     # Список распаршенных ингредиентов 
    
    for ingredient in ingredients:
        ingredient_split = ingredient.rsplit(' - ', 1)
        if len(ingredient_split) == 1:
            parsed_ingredients.append({'name': ingredient_split[0], 'amount': '', 'unit': ''})
            continue
        
        name = ingredient_split[0]
        rest = ingredient_split[1]
        pattern = r"\d+(?:[.,/]\d+)?"
        match = re.search(pattern, rest)

        if match:
            amount = match.group()
            unit = rest.replace(amount, '', 1).strip(' -')
        else:
            unit = rest.strip(' -')
            parsed_ingredients.append({'name': name, 'amount': '', 'unit': unit})
            continue
        parsed_ingredients.append({'name': name, 'amount': amount, 'unit': unit})

    return parsed_ingredients

def insert_recipe(cur, recipe_data: dict) -> int:
    """Функция добавления рецепта в таблицу и получения его id"""
    cur.execute(
        """
        INSERT INTO recipes (name, description, link)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (recipe_data['title'], recipe_data['description'], recipe_data['link'])
    )
    return cur.fetchone()[0]      # Получение возвращаемого id

def insert_steps(cur, recipe_id: int, steps: list[str]) -> None:
    """Функция добавления шагов приготовления в таблицу"""
    steps_list = [(recipe_id, num, instruction) for num, instruction in enumerate(steps, start=1)]
    cur.executemany(
        """
        INSERT INTO steps (recipe_id, step_number, instruction)
        VALUES (%s, %s, %s)
        """,
        steps_list
    )

def get_or_create_ingredient(cur, name: str) -> int:
    """Получение id ингредиента или создание нового"""
    cur.execute(
        """
        INSERT INTO ingredients (name)
        VALUES (%s)
        ON CONFLICT (name)
        DO UPDATE SET name=EXCLUDED.name
        RETURNING id
        """,
        (name, )
    )
    return cur.fetchone()[0]

def insert_recipe_ingredient(cur, recipe_id: int, ingredient_id: int, amount: str, unit: str) -> None:
    """Добавление ингредиентов рецепта в таблицу"""
    cur.execute(
        """
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
        VALUES (%s, %s, %s, %s)
        """,
        (recipe_id, ingredient_id, amount, unit)
    )

def insert_ingredients(cur, recipe_id: int, ingredients: list[dict]) -> None:
    """Оркестратор для добавления ингредиентов в таблицы"""
    for ingredient in ingredients:
        ingredient_id = get_or_create_ingredient(cur, ingredient['name'])
        insert_recipe_ingredient(cur, recipe_id, ingredient_id, ingredient['amount'], ingredient['unit'])

def insert_data(ds):
    """Оркестратор для загрузки данных в базу"""
    try:
        with get_connection_db() as conn:
            with conn.cursor() as cur:
                for recipe in ds:
                    # Добавление данных в таблицу recipes
                    recipe_data = {'title': recipe['title'], 'description': recipe['description'], 'link': recipe['link']}   # Есть значения description == null, будут ли какие-то ошибки при добавлении их в базу?
                    recipe_id = insert_recipe(cur, recipe_data)
                    # Добавление данных в таблицу steps
                    insert_steps(cur, recipe_id, recipe['recipe'])
                    # Парсим ингредиенты
                    parsed_ingredients = parse_ingredients(recipe['ingredients'])
                    # Добавление данных в таблицы ingredients и recipe_ingredients
                    insert_ingredients(cur, recipe_id, parsed_ingredients)
                logger.info("Данные успешно загружены в таблицы")
    except Exception as e:
        logger.error("Ошибка добавления данных в базу: %s", e)
        raise

def main():
    logging.basicConfig(level=logging.INFO)
    ds = load_recipes(limit=1000)
    logger.info("Датасет успешно загружен.")
    insert_data(ds)

if __name__ == "__main__":
    main()        
