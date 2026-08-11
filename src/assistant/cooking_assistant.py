import time
import re
from datetime import datetime, timedelta

from .recipe_loader import RecipeLoader
from .context import AssistantContext, AssistantState
from .commands import COMMANDS
from src.llm.llm_generator import LLMGenerator


class CookingAssistant:
    """Основной класс для сборки всего функционала"""
    def __init__(self, context: AssistantContext, llm: LLMGenerator=None):
        self.context = context
        self.loader = RecipeLoader()        # Рецепты загружаются при старте
        self.llm = llm
        self.timer_end = None       # Время окончания таймера
    
    def process_command(self, text: str) -> str:
        """Основной метод обработки команд"""

        # Класиификация команды
        cmd_id, cmd_data = self._classify(text)
        if cmd_data is None:
            return "Команда не распознана. Повторите, пожалуйста."

        # Проверка состояния
        if self.context.state not in cmd_data["allowed_states"]:
            if self.context.state == AssistantState.IDLE:
                return "Мы ещё не начали готовить. Скажите \"Начать готовить ...\"."
            else:
                return "Сейчас эта команда недоступна."

        # Извлечение параметров
        param = None
        if cmd_data.get("has_parameter"):
            param = self._extract_parameter(text, cmd_data["parameter_type"])
            if param is None:
                return f"Не удалось распознать параметр для команды {cmd_id}. Попробуйте ещё раз."

        # Выполнение действия через диспетчер
        action = getattr(self, f"_{cmd_id}_action", None)
        if action is None:
            return "Внутренняя ошибка: обработчик команды не найден."

        if param is not None:
            return action(param)
        else:
            return action()
        
    # -------- Вспомогательные методы --------
    def _classify(self, text: str):
        """Метод классификации команды"""
        text_lower = text.lower()
        for cmd_id, cmd_data in COMMANDS.items():
            for kw in cmd_data["keywords"]:
                if kw in text_lower:            # Доработать логику проверки
                    return cmd_id, cmd_data
        return None, None

    def _words_to_number(self, words: str) -> float:
        """Метод для преобразования слов в число"""
        # Если уже есть цифры, парсим их
        digits = re.findall(r'\d+\.?\d*', words)
        if digits:
            try:
                return float(digits[0])
            except:
                return None

        # Cловарь с учётом распространённых форм
        NUM_WORDS = {
            # 0-10
            'ноль': 0, 'один': 1, 'одна': 1, 'одного': 1, 'одному': 1, 'одним': 1, 'одном': 1,
            'два': 2, 'две': 2, 'двух': 2, 'двум': 2, 'двумя': 2, 'двух': 2,
            'три': 3, 'трёх': 3, 'трём': 3, 'тремя': 3,
            'четыре': 4, 'четырёх': 4, 'четырём': 4, 'четырьмя': 4,
            'пять': 5, 'пяти': 5, 'пятью': 5,
            'шесть': 6, 'шести': 6, 'шестью': 6,
            'семь': 7, 'семи': 7, 'семью': 7,
            'восемь': 8, 'восьми': 8, 'восемью': 8,
            'девять': 9, 'девяти': 9, 'девятью': 9,
            'десять': 10, 'десяти': 10, 'десятью': 10,
            # 11-19
            'одиннадцать': 11, 'одиннадцати': 11,
            'двенадцать': 12, 'двенадцати': 12,
            'тринадцать': 13, 'тринадцати': 13,
            'четырнадцать': 14, 'четырнадцати': 14,
            'пятнадцать': 15, 'пятнадцати': 15,
            'шестнадцать': 16, 'шестнадцати': 16,
            'семнадцать': 17, 'семнадцати': 17,
            'восемнадцать': 18, 'восемнадцати': 18,
            'девятнадцать': 19, 'девятнадцати': 19,
            # Десятки
            'двадцать': 20, 'двадцати': 20,
            'тридцать': 30, 'тридцати': 30,
            'сорок': 40, 'сорока': 40,
            'пятьдесят': 50, 'пятидесяти': 50,
            'шестьдесят': 60, 'шестидесяти': 60,
            'семьдесят': 70, 'семидесяти': 70,
            'восемьдесят': 80, 'восьмидесяти': 80,
            'девяносто': 90, 'девяноста': 90,
            'сто': 100, 'ста': 100, 'сот': 100, 'стам': 100, 'стами': 100, 'стах': 100,
        }

        # Ищем все слова, которые есть в словаре
        tokens = re.findall(r'[а-яё]+', words.lower())
        numbers = []
        for token in tokens:
            if token in NUM_WORDS:
                numbers.append(NUM_WORDS[token])
            else:
                continue

        if not numbers:
            return None

        # Суммируем все найденные числа
        result = 0
        for n in numbers:
            result += n
        return float(result)

    def _extract_parameter(self, text: str, param_type: str):
        """Метод для извлечения параметров"""
        text_lower = text.lower()

        # Ищем название рецепта
        if param_type == "recipe_name":
            for kw in COMMANDS["start_cooking"]["keywords"]:
                if kw in text_lower:
                    # Берем текст после ключевого слова
                    start = text_lower.find(kw) + len(kw)
                    recipe_name = text[start:].strip()
                    if recipe_name:
                        return recipe_name
            return None
        elif param_type == "number":
            "Ищем число в тексте"
            return self._words_to_number(text_lower)
        elif param_type == "substitution":
            start_word = text_lower[0]              # Ключевое слово замены ("заменить", "вместо", "поменяй")
            parts = text_lower.split(start_word)
            if len(parts) < 2:                      # Если <2, то заменять нечего
                return None
            rest = parts[1].strip()
            if "на" in rest:
                before, after = rest.split("на", 1)
                return {"from": before.strip(), "to": after.strip()}
            return None
        
        return None

    def check_timer(self) -> str:
        """Проверяет, истёк ли таймер, и если да, возвращает сообщение."""
        if self.context.timer_active and self.timer_end and datetime.now() >= self.timer_end:
            self.context.timer_active = False
            self.timer_end = None
            return "Таймер истёк! Время вышло."
        return None

    # -------- Обработчики команд --------
    def _start_cooking_action(self, recipe_name: str) -> str:
        recipe = self.loader.find_recipe(recipe_name)
        if recipe is None:
            all_names = self.loader.get_all_recipe_name()
            return f"Я не нашел блюдо \"{recipe_name}\". Доступные рецепты: {', '.join(all_names)}"

        self.context.current_recipe = recipe
        self.context.current_step_index = 0
        self.context.state = AssistantState.COOKING
        self.context.substitutions = {}
        self.context.scale_factor = 1.0
        self.context.timer_active = False
        self.timer_end = None

        first_step = recipe["steps"][0]
        # Генерация вступления через LLM
        if self.llm:
            intro = self.llm.generate_intro(recipe["name"])
        else:
            intro = "Приступим! Должно получиться очень вкусно!"

        return f"{intro} Шаг 1: {first_step}"

    def _next_step_action(self) -> str:
        recipe = self.context.current_recipe
        if recipe is None:
            return "Нет активного рецепта"
        steps = recipe["steps"]
        self.context.current_step_index += 1

        # Проверяем, закончились ли шаги
        if self.context.current_step_index >= len(steps):
            self.context.state = AssistantState.IDLE
            self.context.current_recipe = None
            return "Все шаги выполнены."
        
        return  f"Шаг {self.context.current_step_index + 1}: {steps[self.context.current_step_index]}"

    def _repeat_step_action(self) -> str:
        recipe = self.context.current_recipe
        if recipe is None:
            return "Нет активного рецепта."
        steps = recipe["steps"]
        idx = self.context.current_step_index
        if idx < 0 or idx >= len(steps):
            return "Нет активного шага."
        return f"Повторяю шаг {idx + 1}: {steps[idx]}"

    def _set_timer_action(self, minutes: float) -> str:
        if minutes <= 0:
            return "Время должно быть положительным числом."
        self.context.timer_active = True
        self.timer_end = datetime.now() + timedelta(minutes=minutes)
        return f"Таймер установлен на {minutes} минут. Я напомню, когда время истечёт."

    def _how_much_time_action(self) -> str:
        if self.timer_end is None or not self.context.timer_active:
            return "Таймер не запущен."
        remaining = self.timer_end - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Таймер уже истёк."
        min = int(remaining.total_seconds() // 60)
        sec = int(remaining.total_seconds() % 60)
        return f"Осталось {min} минут и {sec} секунд."

    def _stop_timer_action(self) -> str:
        if not self.context.timer_active:
            return "Таймер не запущен."
        self.context.timer_active = False
        self.timer_end = None
        return "Таймер остановлен."

    def _substitute_action(self, substitution: dict) -> str:
        from_ing = substitution["from"]
        to_ing = substitution["to"]
        self.context.substitutions[from_ing] = to_ing
        return f"Заменил '{from_ing}' на '{to_ing}'. Учтите это при готовке."

    def _list_ingredients_action(self) -> str:
        recipe = self.context.current_recipe
        if recipe is None:
            return "Нет активного рецепта."
        ingredients = recipe["ingredients"]
        # Учитываем замены и масштабирование
        scale = self.context.scale_factor
        lines = []
        for ing in ingredients:
            name = ing["name"]
            # Если есть замена, используем её
            if name in self.context.substitutions:
                name = self.context.substitutions[name]
            # Применяем масштабирование
            num = re.findall(r"\d+", ing["amount"])
            if not num:
                lines.append(f"{name} - {ing['amount']}")  # Если нет числа, оставляем как есть
                continue
            amount = float(num[0]) * scale
            lines.append(f"{name} - {amount}")   
        if not lines:
            return "Ингредиенты не найдены."
        return "Список ингредиентов: " + ", ".join(lines)

    def _scale_recipe_action(self, num: float) -> str:
        if num <= 0:
            return "Коэффициент должен быть положительным."
        self.context.scale_factor = num
        return f"Порция увеличена в {num} раз. Все количества ингредиентов пересчитаны."

    def _finish_cooking_action(self) -> str:
        recipe = self.context.current_recipe
        if recipe is None:
            return "Нет активного рецепта."
        # Генерируем поздравление через LLM
        if self.llm:
            congrats = self.llm.generate_congratulation(recipe["name"])
        else:
            congrats = "Поздравляю! Блюдо готово, приятного аппетита!"

        self.context.state = AssistantState.IDLE
        self.context.current_recipe = None
        self.context.timer_active = False
        self.timer_end = None

        return congrats

    def _exit_action(self) -> str:
        return "До свидания! Рад был помочь."
