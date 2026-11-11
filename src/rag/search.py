from src.database.db import get_connection_db
from pgvector.psycopg import register_vector
import logging

logger = logging.getLogger(__name__)

def get_query_embedding(model, query: str):
    """Генерирует вектор для поискового запроса пользователя."""
    format_query = f"query: {query}"
    return model.encode(format_query, normalize_embeddings=True)

def find_similar_recipes(cur, query_embedding, limit) -> list[tuple[int, str, str | None, float]]:
    """Поиск подходящих рецептов"""
    cur.execute(
        """
            SELECT id, name, description, (embedding <=> %s) AS distance
            FROM recipes
            ORDER BY distance
            LIMIT %s 
        """,
        (query_embedding, limit)
    )
    return cur.fetchall()       # [(recipe_id (int), recipe_name (str), description (str), distance (float)), ...]

def search_recipes(query: str, model, limit=5) -> list[dict]:
    """Оркестратор, связывающий  модель и бд"""
    try:
        with get_connection_db() as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                rows = find_similar_recipes(cur, get_query_embedding(model, query), limit=limit)
                logger.info("Запрос обработан.")
                retriever_elements = []
                # Преобразование результатов в словарь для дальнейшего использования
                for row in rows:
                    res_dict = {"id": row[0], "name": row[1], "description": row[2], "distance": row[3]}
                    retriever_elements.append(res_dict)
                logger.info("Получены топ-%s релевантных ответов.", limit)
        return retriever_elements
    except Exception as e:
        logger.error("Ошибка на retriever этапе: %s.", e)
        raise
