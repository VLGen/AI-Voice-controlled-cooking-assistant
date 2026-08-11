"""
Инициализация пакета обработки речи.
Содержит модули ASR и TTS.
"""

from .speech_recognizer import SpeechRecognizer
from .tts_engine import TTS

__all__ = [SpeechRecognizer, TTS]