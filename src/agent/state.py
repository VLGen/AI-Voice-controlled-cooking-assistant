from typing import TypedDict, Annotated
from datetime import timedelta
import operator

# Создаем функцию-редьюсер
def keep_last_value(current_value, new_value):
    """Если новое значение пустое (None или []), оставляем старое"""
    if new_value:
        return new_value
    return current_value

class AgentState(TypedDict):
    messages: Annotated[list[dict], operator.add]               # история сообщений
    # Применяю редьюсер ко всем полям
    current_recipe_id: Annotated[int | None, keep_last_value]   # id текущего рецепта                   
    current_step: Annotated[int | None, keep_last_value]        # номер текущего шага                  
    timer_end: Annotated[timedelta | None, keep_last_value]     # таймер
    intent: str                                                 # намерение пользователя
    recipes: Annotated[list[dict], keep_last_value]             # список рецептов
    