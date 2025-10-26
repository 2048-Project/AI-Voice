"""
Система перехвата консольного вывода для интеграции с UI
"""
import sys
import io
import re
from PyQt6.QtCore import QObject, pyqtSignal

# Компилируем регулярные выражения один раз для производительности
PROGRESS_PATTERNS = {
    'fetching': re.compile(r'Fetching \d+ files: (\d+)%'),
    'sampling': re.compile(r'Sampling:\s*(\d+)%'),
    'general': re.compile(r'(\d+)%')
}

# Ключевые слова для быстрой проверки
WARNING_KEYWORDS = {
    'WARNING:', 'Warning:', 'warning:',
    'FutureWarning:', 'UserWarning:',
    'deprecated', 'deprecation'
}

ERROR_KEYWORDS = {
    'ERROR:', 'Error:', 'error:',
    'CRITICAL:', 'Critical:', 'critical:',
    'Exception:', 'Traceback:',
    'Failed:', 'failed:'
}

GENERATION_COMPLETE_KEYWORDS = {
    'forcing EOS token',
    'alignment_stream_analyzer',
    'WARNING:chatterbox.models.t3.inference.alignment_stream_analyzer'
}

IMPORTANT_LOG_KEYWORDS = {
    'loaded', 'Loading', 'loading',
    'Model', 'model', 'Initializing',
    'Generating', 'generating',
    'Complete', 'complete', 'Finished'
}


class ConsoleCapture(QObject):
    """Перехват консольного вывода и извлечение прогресс-информации"""
    
    # Сигналы для отправки данных в UI
    progress_detected = pyqtSignal(int, str)  # процент, сообщение
    log_message = pyqtSignal(str)  # обычное сообщение
    warning_detected = pyqtSignal(str)  # предупреждение
    error_detected = pyqtSignal(str)  # ошибка
    generation_complete = pyqtSignal()  # генерация завершена
    
    def __init__(self):
        super().__init__()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.captured_output = io.StringIO()
        
    def start_capture(self):
        """Начать перехват вывода"""
        sys.stdout = self
        sys.stderr = self
        
    def stop_capture(self):
        """Остановить перехват вывода"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
    def write(self, text):
        """Перехватываем весь вывод"""
        # Сохраняем в оригинальный поток
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # Анализируем текст на предмет прогресс-баров и логов
        self._analyze_output(text)
        
    def flush(self):
        """Обязательный метод для sys.stdout"""
        pass
        
    def _analyze_output(self, text):
        """Анализ вывода на предмет прогресс-баров и важных сообщений"""
        lines = text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            # Проверяем на завершение генерации
            if self._is_generation_complete(line):
                self.generation_complete.emit()
                continue
                
            # Проверяем на прогресс-бары
            progress_info = self._extract_progress(line)
            if progress_info:
                self.progress_detected.emit(progress_info['percentage'], progress_info['message'])
                continue
                
            # Проверяем на предупреждения
            if self._is_warning(line):
                self.warning_detected.emit(line)
                continue
                
            # Проверяем на ошибки
            if self._is_error(line):
                self.error_detected.emit(line)
                continue
                
            # Обычные логи
            if self._is_important_log(line):
                self.log_message.emit(line)
                
    def _extract_progress(self, line):
        """Извлечение информации о прогрессе из строки"""
        # 1. Fetching progress: "Fetching 6 files: 100%|████████| 6/6 [00:00<?, ?it/s]"
        fetching_match = PROGRESS_PATTERNS['fetching'].search(line)
        if fetching_match:
            percentage = int(fetching_match.group(1))
            return {
                'percentage': percentage,
                'message': f"Загрузка файлов: {percentage}%"
            }
            
        # 2. Sampling progress: "Sampling: 12%|██████████████▉| 124/1000 [00:12<01:27, 10.02it/s]"
        sampling_match = PROGRESS_PATTERNS['sampling'].search(line)
        if sampling_match:
            percentage = int(sampling_match.group(1))
            return {
                'percentage': percentage,
                'message': f"Генерация речи: {percentage}%"
            }
            
        # 3. Общие прогресс-бары с процентами
        general_match = PROGRESS_PATTERNS['general'].search(line)
        if general_match and '|' in line and '█' in line:
            percentage = int(general_match.group(1))
            return {
                'percentage': percentage,
                'message': f"Обработка: {percentage}%"
            }
            
        return None
        
    def _is_warning(self, line):
        """Проверка на предупреждения"""
        return any(keyword in line for keyword in WARNING_KEYWORDS)
        
    def _is_error(self, line):
        """Проверка на ошибки"""
        return any(keyword in line for keyword in ERROR_KEYWORDS)
        
    def _is_important_log(self, line):
        """Проверка на важные логи"""
        return any(keyword in line for keyword in IMPORTANT_LOG_KEYWORDS)
        
    def _is_generation_complete(self, line):
        """Проверка на завершение генерации"""
        return any(keyword in line for keyword in GENERATION_COMPLETE_KEYWORDS)


# Глобальный экземпляр для использования в других модулях
console_capture = ConsoleCapture()
