import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from src.embeddings.model import load_model
from src.rag.generate import generate_answer
from src.rag.search import search_recipes

class RecipeAgent():


    def __init__(self):
        """Инициализация модели и системного промпта"""
        self.logger = logging.getLogger(__name__)
        self.env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=self.env_path)
        self.model = os.getenv("LLM")
        self.embedd_model = load_model()
        if not self.model:
            self.logger.error("Ошибка загрузки llm")
            raise ValueError("LLM не задан в .env")
        self.system_prompt = Path(__file__).parents[0] / "prompts" / "system_prompt.md"
        self.system_prompt_text = self.system_prompt.read_text(encoding="utf-8")
        self.history = []
        
    
    def get_answer(self, query: str):
        """получение ответа от LLM"""
        recipes = search_recipes(query, model=self.embedd_model)

        if not recipes:
            answer = "К сожалению я не нашел рецепты в базе по вашему запросу. Попробуйте переформулировать."
        else:
            answer = generate_answer(query, model=self.model, system_prompt=self.system_prompt_text, recipes=recipes, history=self.history)
            
        self.history.append({'role': 'user', 'content': query})     # Добавление запроса в историю сообщений
        self.history.append({'role': 'assistant', 'content': answer})       # Добавление ответа в историю сообщений
        self.history = self.history[-10:]
        return answer
