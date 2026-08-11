from enum import Enum

class AssistantState(Enum):
    """Класс для хранения состояний"""
    
    IDLE = "idle"
    COOKING = "cooking"

class AssistantContext:
    """Класс контекста. Хранит состояние сессии"""

    def __init__(self):
        self.state = AssistantState.IDLE    # По дефолту состояние IDLE
        self.timer_active = False           # Включен ли таймер
        self.timer_end_time = None          # Время окончания таймера в datetime
        self.current_recipe = None          # Выбранный рецепт
        self.current_step_index = 0         # Текущий шаг
        self.scale_factor = 1.0             # Коэффициент размера порции. 1.0 - стандартная по рецепту
        self.substitutions = {}             # Замены ({"ингредиент": "замена"})
        self.last_question = None           # Последний вопрос