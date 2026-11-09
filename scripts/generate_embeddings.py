from pgvector.psycopg import register_vector
from src.database.db import get_connection_db
from src.embeddings.model import load_model
import logging

logger = logging.getLogger(__name__)

def get_recipe_and_ingredients(cur) -> list[tuple[int, str, list[str]]]:
    """Отправление запроса в бд для получения айди, названия и ингредиентов рецепта"""
    cur.execute(
        """
            SELECT r.id, r.name, array_agg(i.name) AS ingredient_names
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON ri.recipe_id = r.id
            LEFT JOIN ingredients i ON i.id = ri.ingredient_id
            WHERE r.embedding IS NULL
            GROUP BY r.id, r.name
            LIMIT 1000
        """
    )
    return cur.fetchall()       # Получаем список кортежей вида [(recipe_id (int), recipe_name (str), recipe_ingredients (list[str])), ...]

def format_string(row: tuple[int, str, list[str]]) -> str:
    """Формирование строки для эмбеддинга из кортежа"""
    string = f"passage: Название: {row[1]}. Ингредиенты: "
    string += ", ".join(row[2])
    return string

def create_embedding(cur, model):
    """Генерация эмбеддингов"""
    rows = get_recipe_and_ingredients(cur)
    for row in rows:
        yield (row[0], model.encode(format_string(row), normalize_embeddings=True))

def add_embedding(model):
    """Добавление эмбеддингов в базу данных"""
    try:
        with get_connection_db() as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                count_embedding = 0     # Счетчик количества добавленных эмбеддингов. Понадобится в будущем
                for recipe_id, embedding in create_embedding(cur, model):
                    # Запрос на добавление эмбеддинга в таблицу recipes
                    cur.execute(
                        """
                            UPDATE recipes SET embedding = %s WHERE id = %s     
                        """,
                        (embedding, recipe_id)
                    )
                    count_embedding += 1
                    if count_embedding % 100 == 0:
                        logger.info("Вектор для рецепта %s добавлен в базу.", recipe_id)
                        logger.info("Всего добавлено %s векторов.", count_embedding)
                logger.info("Всего обработано %s рецептов", count_embedding)
    except Exception as e:
        logger.error("Ошибка на этапе векторизации: %s", e)
        raise

def main():
    logging.basicConfig(level=logging.INFO)
    model = load_model()
    logger.info("Модель эмбеддингов успешно загружена")
    add_embedding(model)

if __name__ == "__main__":
     main()