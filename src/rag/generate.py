import logging
import os
from dotenv import load_dotenv
from ollama import chat
from pathlib import Path


logger = logging.getLogger(__name__)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

def format_recipes_to_text(recipes: list[dict]) -> str:
    """Форматирование рецептов в строку"""

    result = ""
    for recipe in recipes:
        id = recipe["id"]
        name = recipe["name"]
        desc = recipe["description"]
        result += f"Рецепт {id}: {name}.\n"
        if desc:
            result += f"Описание: {desc}.\n\n"
        else:
            result += f"Описание: отсутствует.\n\n"
    return result

def generate_answer(query: str, model: str, system_prompt: str, recipes: list[dict], history: list[dict]) -> str:
    """Передача промпта в LLM"""
    format_recipes = format_recipes_to_text(recipes)
    user_content = f"""
    <user_query>
    {query}
    </user_query>

    <recipes>
    {format_recipes}
    </recipes>
    """
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_content})

    response = chat(model=model, messages=messages)
    return response.message.content