from .context import AssistantState
"""Список команд и их метаданные"""

COMMANDS = {
    "start_cooking": {"keywords": ["начать готовить", "готовим", "давай готовить"],     # Ключевые фразы
                      "allowed_states": [AssistantState.IDLE],                          # Допустимые состояния
                      "has_parameter": True,                                            # Содержание параметров
                      "parameter_type": "recipe_name",                                  # Тип параметров
                      "action": "start_cooking_action"                                  # Вызов функции, соответствующей значению
                    },
    "next_step": {
                    "keywords": ["следующий шаг", "дальше", "продолжить"],
                    "allowed_states": [AssistantState.COOKING],
                    "has_parameter": False,
                    "action": "next_step_action"
                  },
    "repeat_step": {
                        "keywords": ["повтори шаг", "повтори", "еще раз"],
                        "allowed_states": [AssistantState.COOKING],
                        "has_parameter": False,
                        "action": "repeat_step_action"
                  },
    "set_timer": {
                    "keywords": ["поставь таймер", "таймер на", "запусти таймер"],
                    "allowed_states": [AssistantState.COOKING],
                    "has_parameter": True,
                    "parameter_type": "number",   # Извлекаем минуты
                    "action": "set_timer_action"},
    "how_much_time": {  
                        "keywords": ["сколько осталось", "осталось времени", "время"],
                        "allowed_states": [AssistantState.COOKING],
                        "has_parameter": False,
                        "action": "how_much_time_action"
                    },
    "stop_timer": {
                    "keywords": ["стоп таймер", "останови таймер", "отмени таймер"],
                    "allowed_states": [AssistantState.COOKING],
                    "has_parameter": False,
                    "action": "stop_timer_action"
                },
    "substitute": {
                    "keywords": ["замени", "вместо", "поменяй"],
                    "allowed_states": [AssistantState.COOKING],
                    "has_parameter": True,
                    "parameter_type": "substitution",   # Что на что поменять
                    "action": "substitute_action"
                },
    "list_ingredients": {
                            "keywords": ["ингредиенты", "список продуктов", "что понадобится"],
                            "allowed_states": [AssistantState.COOKING],
                            "has_parameter": False,
                            "action": "list_ingredients_action"
                        },
    "scale_recipe": {
                        "keywords": ["увеличь порцию", "добавь граммовки"],
                        "allowed_states": [AssistantState.COOKING],
                        "has_parameter": True,
                        "parameter_type": "number",  # На сколько увеличить
                        "action": "scale_recipe_action"
                    },
    "finish_cooking": {
                        "keywords": ["готово", "закончил", "приготовил"],
                        "allowed_states": [AssistantState.COOKING],
                        "has_parameter": False,
                        "action": "finish_cooking_action"
                    },
    "exit": {
                "keywords": ["выйти", "завершить", "отмена"],
                "allowed_states": [AssistantState.IDLE, AssistantState.COOKING],
                "has_parameter": False,
                "action": "exit_action"
            }
}