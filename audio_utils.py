"""
Утилиты для работы с аудио
"""
import wave
from pathlib import Path


def get_audio_duration(file_path):
    """
    Получение длительности WAV файла через стандартную библиотеку wave
    """
    file_path_str = str(file_path)
    
    # Проверяем, что файл не пустой
    if Path(file_path).stat().st_size == 0:
        return 0
        
    with wave.open(file_path_str, 'rb') as wav_file:
        nframes = wav_file.getnframes()
        framerate = wav_file.getframerate()
        duration = nframes / float(framerate)
        return round(duration, 3)  # Округляем до миллисекунд


def calculate_voice_accuracy(duration, optimal_duration=15.0):
    """
    Расчет точности голоса на основе длительности
    """
    if duration >= optimal_duration:
        excess_percent = ((duration - optimal_duration) / optimal_duration) * 100
        return 100.0, f"+{excess_percent:.0f}%"
    else:
        accuracy = (duration / optimal_duration) * 100
        return min(accuracy, 100.0), f"{accuracy:.0f}%"


def get_voice_accuracy_info(voice_file, optimal_duration=15.0):
    """
    Получение информации о точности голоса из файла
    """
    duration = get_audio_duration(voice_file)
    return calculate_voice_accuracy(duration, optimal_duration)