import time

from src.assistant.context import AssistantContext
from src.assistant.cooking_assistant import CookingAssistant
from src.speech.speech_recognizer import SpeechRecognizer
from src.speech.tts_engine import TTS
from src.llm.llm_generator import LLMGenerator

def main():
    context = AssistantContext()
    llm = LLMGenerator()
    assistant = CookingAssistant(context, llm=llm)
    recognizer = SpeechRecognizer()
    tts = TTS()

    print("Голосовой помощник запущен. Скажите \"Начать готовить...\"")

    while True:

        # Проверка таймера
        timer_msg = assistant.check_timer()
        if timer_msg:
            tts.speak(timer_msg)
            # После сообщения о таймере продолжаем работу
            continue

        # Распознавание речи
        command_text = recognizer.recognize_from_microphone(duration=10, silence_timeout=2)
        if command_text is None:
            tts.speak("Комманда не опознана. Повторите, пожалуйста.")
            continue

        # Обработка команды
        response = assistant.process_command(command_text)
        if response:
            tts.speak(response)

        if "До свидания" in response:
            print("Завершение работы.")
            break

        # Небольшая пауза перед следующим циклом
        time.sleep(0.2)

if __name__ == "__main__":
    main()