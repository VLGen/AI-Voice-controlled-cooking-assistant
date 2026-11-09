import logging
from .db import get_connection_db
from .schema import CREATE_EXTENSION, CREATE_RECIPES_TABLE, CREATE_INGREDIENTS_TABLE, CREATE_RECIPE_INGREDIENTS_TABLE, CREATE_STEPS_TABLE

logger = logging.getLogger(__name__)

def create_tables():
    try:
        with get_connection_db() as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_EXTENSION)
                cur.execute(CREATE_RECIPES_TABLE)
                cur.execute(CREATE_INGREDIENTS_TABLE)
                cur.execute(CREATE_RECIPE_INGREDIENTS_TABLE)
                cur.execute(CREATE_STEPS_TABLE)
        logger.info("Все таблицы успешно созданы.")
    except Exception as e:
        logger.error("Ошибка при создании таблиц.\n%s", e)
        raise
