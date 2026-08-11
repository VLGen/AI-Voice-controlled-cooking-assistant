import pyttsx3

class TTS:
    def __init__(self, rate=150):
        """
        Инициализация TTS. Сохраняем настройки, но движок создаём при каждом speak.
        """
        self.rate = rate
        self.voice_id = None
        # Попробуем найти русский голос один раз при инициализации
        temp_engine = pyttsx3.init()
        voices = temp_engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower() or 'русский' in voice.name.lower():
                self.voice_id = voice.id
                break
        temp_engine.stop()
        print("TTS инициализирован (pyttsx3).")

    def speak(self, text: str):
        """Синтезирует и воспроизводит речь, создавая новый движок."""
        print(f"TTS: {text}")
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', 1.0)
        if self.voice_id:
            engine.setProperty('voice', self.voice_id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()  # явно останавливаем движок после завершения