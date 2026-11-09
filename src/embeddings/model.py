import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

def load_model() -> SentenceTransformer:
    name = os.getenv("EMBEDDING_MODEL")
    if not name:
        logger.error("Ошибка загрузки модели эмбеддингов")
        raise ValueError("EMBEDDING_MODEL не задан в .env")
    return SentenceTransformer(name)