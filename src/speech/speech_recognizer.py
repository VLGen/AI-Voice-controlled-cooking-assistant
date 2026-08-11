import sys
import json
import time
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

class SpeechRecognizer:
    def __init__(self, model_path="models/vosk_model"):
        print("Загрузка модели Vosk...")
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)        # Частота дискретизации 16000
            # Будем получать частичные результаты
            self.recognizer.SetWords(True)
            print("Модель загружена.")
        except Exception as e:
            print(f"Ошибка загрузка модели Vosk: {e}")
            print("Убедитесь, что папка 'vosk_model' существует и содержит файлы модели")
            sys.exit(1)

    def recognize_from_microphone(self, duration=5, silence_timeout=2) -> str:
        """
        Записывает звук с микрофона и распознает речь.
        @param duration: Максимальная длительность записи в секундах.
        @param silence_timeout: Таймаут молчания в секундах, после которого запись прекращается.
        @return: Распознанный текст или None, если ничего не распознано
        """
        print("Слушаю...")

        samplerate = 16000          # Настройка аудио потока: моно, 16 кГц
        block_size = 8000           # Размер блоков аудиоданных, которые мы будем получать
        audio_data = []             # Список для хранения аудиоданных
        silence_start = None        # Начало молчания
        start_time = time.time()    # Время начала записи
        recording = True            # Флаг процесса записи. True - запись идет

        def callback(indata, frames, time_info, status):
            """
            Функция обработки блоков аудиоданных
            @param indata: numpy-массив с аудиоданными (frames, channels).
            @param frames: количество семплов в текущем блоке.
            @param time_info: словарь с информацией о времени.
            @param status: код состояния 
            """
            nonlocal audio_data, silence_start, recording

            if status:
                print(f"Ошибка аудиопотока: {status}", file=sys.stderr)

            # Конвертируем значения из диапазона [-1, 1] в int16
            int_data = (indata * 32767).astype(np.int16)
            # Добавляем текущий блок данных к общему списку.
            # Таким образом, собираем полный аудиофрагмент и
            # затем передадим его только один раз после завершения записи 
            audio_data.append(int_data)

            # Проверяем уровень громкости для обнаружения молчания.
            # Вычисляем RMS для текущего блока
            rms = np.sqrt(np.mean(indata**2))
            if rms < 0.01:     # Порог тишины
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > silence_timeout:
                    print("Завершаю запись.")
                    recording = False
            else:
                silence_start = None

        # Запуск записи с микрофона
        try:
            # Запускаем поток записи с помощью InputStream
            # samplerate - частота записи
            # channels - количество каналов (у нас моно)
            # callbacks - функция, которая вызывается автоматически при поступлении нового блока данных
            # blocksize - размер поступающего блока данных
            with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=block_size):
                while recording:
                    if time.time() - start_time > duration:
                        print("Превышена максимальная длительность записи")
                        recording = False
                        break
                    sd.sleep(100)   # Ожидание завершения работы callback
        except Exception as e:
            print(f"Ошибка при записи с микрофона: {e}")
            return None

        if not audio_data:
            print("Не удалось записать аудио")
            return None

        # Объединяем все блоки в один массив и конвертируем в bytes
        full_audio = np.concatenate(audio_data, axis=0)
        full_audio = full_audio.tobytes()

        print("Обработка аудио...")
        # Передаем аудио в распознаватель
        if self.recognizer.AcceptWaveform(full_audio):
            # Получение финального результата из json-файла
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"Распознано: {text}")
                return text
            else:
                print("Речь не распознана")
                return None
        else:
            # Если финального результата нет, пробуем получить частичный
            partial = json.loads(self.recognizer.PartialResult())
            text = partial.get("partial", "")
            if text:
                print(f"Частично распознано: {text}")
                return text
            else:
                print("Речь не распознана")
                return None

if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    command = recognizer.recognize_from_microphone(duration=10, silence_timeout=2)
    if command:
        print(f"Итоговая команда: {command}")
    else:
        print("Команда не распознана")
