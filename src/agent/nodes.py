import os
import logging
import re
from src.agent.recipe_agent import RecipeAgent
from src.agent.state import AgentState
from src.rag.steps import get_recipe_steps
from pathlib import Path
from dotenv import load_dotenv
from ollama import chat

logger = logging.getLogger(__name__)                                           # логирование
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
MODEL = os.getenv("LLM")                                                      # модель LLM
ROUTER_PROMPT = Path(__file__).parents[0] / "prompts" / "router_prompt.md"    # путь к промпту для определения намерения
ROUTER_PROMPT_TEXT = ROUTER_PROMPT.read_text(encoding="utf-8")                # текст промпта для определения намерения
SELECT_PROMPT = Path(__file__).parents[0]/ "prompts" / "select_prompt.md"     # путь к промпту для выбора рецепта
SELECT_PROMPT_TEXT = SELECT_PROMPT.read_text(encoding="utf-8")                # текст промпта для выбора рецепта
recipe_agent = RecipeAgent(llm=MODEL)


def router_node(state: AgentState) -> dict:
    """Получение намерения из запроса"""
    last_message = state["messages"][-1]["content"]
    normalized_message = last_message.lower()

    # Проверка на ключевые слова для перехода к предыдущему или следующему шагу
    if re.search(
        r"\b(?:назад|предыдущ\w*|прошл\w*|вернись|вернуться|верни)\b",
        normalized_message,
    ):
        logger.info("Намерение пользователя определено: previous_step")
        return {"intent": "previous_step"}
    if re.search(r"\b(?:дальше|следующ\w*)\b", normalized_message):
        logger.info("Намерение пользователя определено: next_step")
        return {"intent": "next_step"}

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": ROUTER_PROMPT_TEXT},
            *state["messages"][-3:] 
        ],
        options={"num_ctx": 8192},
    )
    intent = response.message.content.strip().lower()
    logger.info("Намерение пользователя определено: %s", intent)
    return {"intent": intent}

def recipe_node(state: AgentState) -> dict:
    """Поиск рецепта"""
    query = state["messages"][-1]["content"]
    # Текущий запрос уже уйдёт в generate_answer отдельно, в историю — только прошлые реплики
    history = state["messages"][:-1][-10:]
    answer = recipe_agent.get_answer(query, history=history)
    recipes = recipe_agent.recipes
    logger.info(f"Найдено рецептов: {len(recipes)}")
    return {
        "messages": [{"role": "assistant", "content": answer}],
        "recipes": recipes,
    }

def route_decision(state: AgentState) -> str:
    """Выбор следующего узла"""
    if "find_recipe" in state["intent"]:
        return "recipe_node"
    elif "select_recipe" in state["intent"]:
        return "select_node"
    elif "previous_step" in state["intent"] or "next_step" in state["intent"]:
        return "step_node"
    return "end_node"

def select_node(state: AgentState) -> dict:
    """Выбор рецепта"""
    query = state["messages"][-1]["content"]
    recipes = state["recipes"]
    
    # Достаем предыдущий ответ ассистента
    previous_answer = ""
    if len(state["messages"]) >= 2:
        previous_answer = state["messages"][-2]["content"]

    # Формируем текст с рецептами для LLM
    recipes_text = "\n".join(
        f"[{index}] {recipe['name']}"
        for index, recipe in enumerate(recipes)
    )

    # Собираем запрос для LLM
    user_content = f"""Предыдущий ответ ассистента (для контекста):
    {previous_answer}

    Список рецептов:
    {recipes_text}

    Запрос пользователя: {query}"""

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SELECT_PROMPT_TEXT},
            {"role": "user", "content": user_content},
        ],
        options={"num_ctx": 8192}
    )
    answer = (response.message.content or "").strip()
    logger.info("\n[DEBUG] Сырой ответ LLM в select_node: '%s'\n", answer) 

    match = re.search(r'\d+', answer)
    if match:
        selected_index = int(match.group())
    else:
        selected_index = -1

    print(f"[DEBUG] len(recipes) = {len(recipes)}")
    # Проверяем корректность выбранного индекса
    if selected_index < 0 or selected_index >= len(recipes):
        return {
            "messages": [{
                "role": "assistant",
                "content": "Я не понял, какой рецепт вы выбрали. Пожалуйста, повторите еще раз.",
            }]
        }
    recipe = recipes[selected_index]
    return {
        "current_recipe_id": recipe["id"],
        "messages": [{
            "role": "assistant",
            "content": f"Отлично! Вы выбрали {recipe['name']}. Теперь мы можем приступать к приготовлению. Дайте знать, когда будете готовы, и я расскажу вам пошаговый рецепт.",
        }],
    }

def step_node(state: AgentState) -> dict:
    """Обработка шагов рецепта"""

    # Получаем текущий рецепт и шаг
    recipe_id = state.get("current_recipe_id")
    if recipe_id is None:
        return {
            "messages": [{
                "role": "assistant",
                "content": "Пожалуйста, выберите рецепт перед тем, как мы начнем готовить.",
            }]
        }

    # Получаем шаги рецепта из базы данных
    steps = get_recipe_steps(recipe_id)
    if not steps:
        return {
            "messages": [{
                "role": "assistant",
                "content": "Извините, я не смог найти шаги для этого рецепта.",
            }]
        }

    current_step = state.get("current_step") or 1
    if state["intent"] == "previous_step":
        current_step = max(1, current_step - 2)

    if current_step > len(steps):
        return {
            "messages": [{
                "role": "assistant",
                "content": "Вы уже завершили все шаги рецепта. Приятного аппетита!",
            }]
        }

    # Получаем текущий шаг и формируем ответ
    step = steps[current_step - 1]
    return {
        "current_step": current_step + 1,
        "messages": [{
            "role": "assistant",
            "content": f"Шаг {current_step} из {len(steps)}: {step['instruction']}",
        }],
    }