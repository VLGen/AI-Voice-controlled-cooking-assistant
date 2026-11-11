import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from src.embeddings.model import load_model
from src.rag.generate import generate_answer
from src.rag.search import search_recipes

class RecipeAgent():


    def __init__(self, llm: str):
        """Инициализация модели и системного промпта"""
        self.logger = logging.getLogger(__name__)
        self.env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=self.env_path)
        self.model = llm
        self.embedd_model = load_model()
        if not self.model:
            self.logger.error("Ошибка загрузки llm")
            raise ValueError("LLM не задан в .env")
        self.system_prompt = Path(__file__).parents[0] / "prompts" / "system_prompt.md"
        self.system_prompt_text = self.system_prompt.read_text(encoding="utf-8")
        
    def get_recipes(self, query: str):
        """Получение списка рецептов"""
        return search_recipes(query, model=self.embedd_model)

    def get_answer(self, query: str, history: list[dict] | None = None):
        """Получение ответа от LLM"""
        self.recipes = self.get_recipes(query)
        return generate_answer(
            query,
            model=self.model,
            system_prompt=self.system_prompt_text,
            recipes=self.recipes,
            history=history or [],
        )
