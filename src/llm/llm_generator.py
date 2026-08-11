from transformers import AutoTokenizer, AutoModelForCausalLM

class LLMGenerator:
    def __init__(self, model_name="Vikhrmodels/Vikhr-Qwen-2.5-0.5b-Instruct", max_new_tokens=30):
        print(f"Загружаю {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.max_new_tokens = max_new_tokens
        # Если у модели нет pad_token, задаём eos_token как pad
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Модель загружена.")

    def clean_generated(self, text: str, default: str) -> str:
        # Если текст пустой или слишком короткий - вовращаем дефолтную фразу
        if not text or len(text) < 3:
            return default
        # Убираем кавычки
        text = text.strip('«»" \n')
        # Выводим только одно законченное предложение
        for sep in ['.', '!', '?']:
            if sep in text:
                text = text.split(sep)[0] + sep
                break
        # Если текст слишком длинный - обрезаем
        if len(text) > 80:
            text = text[:80].rsplit(' ', 1)[0] + '...'
        return text.strip() if len(text) >= 3 else default

    def generate(self, user_content: str) -> str:
        messages = [{"role": "user", "content": user_content}]
        # Применяем шаблон чата
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=0.4,
            top_p=0.9,
        )
        # Декодируем только новые токены
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response.strip()

    def generate_intro(self, recipe_name: str) -> str:
        user_content = (
            f"Ты — повар-помощник. Приготовь блюдо {recipe_name}.\n"
            f"Напиши одно короткое воодушевляющее предложение (не более 10 слов)."
        )
        raw = self.generate(user_content)
        return self.clean_generated(raw, "Приступим! Будет вкусно!")

    def generate_congratulation(self, recipe_name: str) -> str:
        user_content = (
            f"Блюдо {recipe_name} готово! Ты — повар-помощник.\n"
            f"Коротко похвали пользователя, пожелай приятного аппетита."
        )
        raw = self.generate(user_content)
        return self.clean_generated(raw, "Поздравляю! Отличная работа!")