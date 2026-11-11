from src.database.db import get_connection_db
from pgvector.psycopg import register_vector
import logging

logger = logging.getLogger(__name__)

def get_recipe_steps(recipe_id: int) -> list[dict]:
    """Получение шагов рецепта из базы данных"""
    try:
        with get_connection_db() as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT instruction FROM steps WHERE recipe_id = %s ORDER BY step_number""",
                    (recipe_id,)
                )
                rows = cur.fetchall()
                logger.info("Шаги приготовления успешно получены из базы.")
                return [{"instruction": row[0]} for row in rows]
    except Exception as e:
        logger.error("Ошибка извлечения шагов приготовления из базы: %s", e)
        raise