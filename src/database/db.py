import os
from dotenv import load_dotenv
import psycopg
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection_db():
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT")
    host = "localhost"

    variables = [
        ("POSTGRES_USER", user),
        ("POSTGRES_PASSWORD", password),
        ("POSTGRES_DB", db_name),
        ("POSTGRES_PORT", port)
    ]
    for name, val in variables:
        if val is None:
            raise ValueError(f"{name} не задан в .env файле")

    try:
        return psycopg.connect(user=user, dbname=db_name, password=password, host=host, port=port)
    except Exception as e:
        logger.error(f"Ошибка соединения с базой данных: {e}")
        raise
