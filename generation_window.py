from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QCheckBox,
                             QLineEdit, QProgressBar, QMessageBox, QApplication,
                             QTextBrowser, QDialog, QComboBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from styles import AppStyles
from voice import VoiceGenerator
from console_capture import console_capture
import torch

# Константы для стилей прогресс-бара
PROGRESS_BAR_STYLES = {
    'success': """
        QProgressBar {
            border: 2px solid #38A169;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            color: #FFFFFF;
        }
        QProgressBar::chunk {
            background: #38A169;
            border-radius: 6px;
        }
    """,
    'error': """
        QProgressBar {
            border: 2px solid #E53E3E;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            color: #FFFFFF;
        }
        QProgressBar::chunk {
            background: #E53E3E;
            border-radius: 6px;
        }
    """
}


class SettingsDialog(QDialog):
    """Простое окно настроек генерации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(250, 150)
        self.setModal(True)
        
        # Установка иконки
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Устройство - стильный переключатель табов
        device_layout = QVBoxLayout()
        
        # Контейнер для табов
        tabs_container = QWidget()
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)
        
        # Кнопки табов
        self.cpu_tab = QPushButton("CPU")
        self.gpu_tab = QPushButton("GPU")
        
        # Настройка размеров
        self.cpu_tab.setFixedHeight(30)
        self.gpu_tab.setFixedHeight(30)
        
        # Стили для табов
        self.cpu_tab.setStyleSheet("""
            QPushButton {
                border: 1px solid #CBD5E0;
                border-right: none;
                background: #F7FAFC;
                color: #2D3748;
                font-weight: bold;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }
            QPushButton:hover {
                background: #EDF2F7;
            }
            QPushButton:pressed {
                background: #E2E8F0;
            }
        """)
        
        self.gpu_tab.setStyleSheet("""
            QPushButton {
                border: 1px solid #CBD5E0;
                background: #F7FAFC;
                color: #2D3748;
                font-weight: bold;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background: #EDF2F7;
            }
            QPushButton:pressed {
                background: #E2E8F0;
            }
        """)
        
        # Подключаем клики
        self.cpu_tab.clicked.connect(self.select_cpu)
        self.gpu_tab.clicked.connect(self.select_gpu)
        
        tabs_layout.addWidget(self.cpu_tab)
        tabs_layout.addWidget(self.gpu_tab)
        
        device_layout.addWidget(tabs_container)
        
        # Язык
        language_layout = QHBoxLayout()
        language_label = QLabel("Язык:")
        
        # Выпадающий список для языка
        self.language_combo = QComboBox()
        self.language_combo.addItems(["ru", "en"])
        self.language_combo.setCurrentIndex(0)  # По умолчанию ru
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        
        # Кнопки
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Отмена")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # Сборка
        layout.addLayout(device_layout)
        layout.addLayout(language_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Инициализация значений
        self.cuda_available = torch.cuda.is_available()
        self.device_index = 0 if self.cuda_available else 1
        self.language_index = 0
        self.devices = ["GPU", "CPU"]
        self.languages = ["ru", "en"]
        
        # Устанавливаем начальное состояние табов
        self.update_device_tabs()
        self.language_combo.setCurrentIndex(self.language_index)
        
        # Блокируем GPU если CUDA недоступна
        if not self.cuda_available:
            self.gpu_tab.setEnabled(False)
            self.gpu_tab.setStyleSheet("""
                QPushButton {
                    border: 1px solid #E2E8F0;
                    background: #F7FAFC;
                    color: #A0AEC0;
                    font-weight: bold;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)
    
    def select_cpu(self):
        """Выбор CPU"""
        self.device_index = 1
        self.update_device_tabs()
    
    def select_gpu(self):
        """Выбор GPU"""
        if self.cuda_available:
            self.device_index = 0
            self.update_device_tabs()
    
    def update_device_tabs(self):
        """Обновление стилей табов устройств"""
        if self.device_index == 0:  # GPU выбран
            self.gpu_tab.setStyleSheet("""
                QPushButton {
                    border: 1px solid #4299E1;
                    background: #4299E1;
                    color: white;
                    font-weight: bold;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)
            self.cpu_tab.setStyleSheet("""
                QPushButton {
                    border: 1px solid #CBD5E0;
                    border-right: none;
                    background: #F7FAFC;
                    color: #2D3748;
                    font-weight: bold;
                    border-top-left-radius: 5px;
                    border-bottom-left-radius: 5px;
                }
                QPushButton:hover {
                    background: #EDF2F7;
                }
            """)
        else:  # CPU выбран
            self.cpu_tab.setStyleSheet("""
                QPushButton {
                    border: 1px solid #4299E1;
                    background: #4299E1;
                    color: white;
                    font-weight: bold;
                    border-top-left-radius: 5px;
                    border-bottom-left-radius: 5px;
                }
            """)
            self.gpu_tab.setStyleSheet("""
                QPushButton {
                    border: 1px solid #CBD5E0;
                    background: #F7FAFC;
                    color: #2D3748;
                    font-weight: bold;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
                QPushButton:hover {
                    background: #EDF2F7;
                }
            """)
    
    def on_language_changed(self, index):
        """Обработчик изменения языка в выпадающем списке"""
        self.language_index = index
    
    def get_device(self):
        """Получить выбранное устройство"""
        return "cuda" if self.devices[self.device_index] == "GPU" else "cpu"
    
    def get_language(self):
        """Получить выбранный язык"""
        return self.languages[self.language_index]


class GenerationWorker(QThread):
    """Поток для генерации речи"""
    progress_updated = pyqtSignal(int, str)  # процент, сообщение
    generation_finished = pyqtSignal(bool, str, str)  # success, message, file_path

    def __init__(self, text, voice_path, play_after, save_file, filename, device="cuda", language="ru"):
        super().__init__()
        self.text = text
        self.voice_path = voice_path
        self.play_after = play_after
        self.save_file = save_file
        self.filename = filename
        self.device = device
        self.language = language
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        # Начинаем перехват консольного вывода
        console_capture.start_capture()
        
        try:
            # Этап 1: Инициализация генератора
            self.progress_updated.emit(5, "Запуск программы...")
            if not self.is_running:
                return

            voice_generator = VoiceGenerator(device=self.device, language=self.language)

            # Этап 2: Загрузка модели (если нужно)
            self.progress_updated.emit(15, "Загрузка модели TTS...")
            if not self.is_running:
                return

            # Генерация речи с отслеживанием прогресса
            self.progress_updated.emit(25, "Подготовка текста...")
            if not self.is_running:
                return

            # Генерация речи
            audio, sr, gen_time = voice_generator.generate_speech(
                text=self.text,
                reference_file=self.voice_path
            )

            if audio is None:
                self.generation_finished.emit(False, "Ошибка генерации: не удалось сгенерировать аудио", "")
                return

            if not self.is_running:
                return

            # Этап 3: Обработка результатов
            self.progress_updated.emit(85, "Обработка результатов...")

            result_message = ""

            # Воспроизведение
            if self.play_after and self.is_running:
                self.progress_updated.emit(90, "Воспроизведение аудио...")
                play_success = voice_generator.play_audio(audio, sr)
                if play_success:
                    result_message += "Аудио воспроизведено. "
                else:
                    result_message += "Ошибка воспроизведения. "

            # Сохранение
            if self.save_file and self.is_running:
                self.progress_updated.emit(95, "Сохранение файла...")
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                filepath = output_dir / f"{self.filename}.wav"
                save_success = voice_generator.save_audio(audio, sr, str(filepath))
                if save_success:
                    result_message += f"Файл сохранен как: {self.filename}.wav"
                else:
                    result_message += "Ошибка сохранения файла."

            # Завершение
            if self.is_running:
                self.progress_updated.emit(100, "Генерация завершена!")
                file_path = str(filepath) if self.save_file and save_success else ""
                self.generation_finished.emit(True, result_message.strip(), file_path)

        except Exception as e:
            if self.is_running:
                self.generation_finished.emit(False, f"Ошибка генерации: {str(e)}", "")
        finally:
            # Останавливаем перехват консольного вывода
            console_capture.stop_capture()


class GenerationWindow(QMainWindow):
    def __init__(self, voice_path, voice_name):
        super().__init__()
        self.voice_path = voice_path
        self.voice_name = voice_name
        self.generation_thread = None
        self.progress_timer = None
        self.current_progress = 0
        
        # Настройки по умолчанию
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.language = "ru"
        
        self.setup_ui()
        
    def _connect_console_signals(self):
        """Подключение сигналов консольного вывода"""
        console_capture.progress_detected.connect(self.on_console_progress)
        console_capture.generation_complete.connect(self.on_generation_complete)
        
    def _disconnect_console_signals(self):
        """Отключение сигналов консольного вывода"""
        console_capture.progress_detected.disconnect()
        console_capture.generation_complete.disconnect()

    def setup_ui(self):
        self.setWindowTitle("Генератор речи")
        self.setMinimumSize(800, 600)
        
        # Установка иконки окна
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Верхняя панель с кнопкой назад и названием голоса
        header_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setFixedHeight(35)
        self.back_btn.setStyleSheet(AppStyles.get_button_style("back"))
        self.back_btn.clicked.connect(self.go_back)

        voice_label = QLabel(f"Голос: {self.voice_name}")
        voice_label.setStyleSheet("""
            color: #2D3748;
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
        """)
        voice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка настроек (SVG иконка)
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(35, 35)
        
        # Загружаем SVG иконку
        settings_icon_path = Path("assets/settings.svg")
        if settings_icon_path.exists():
            self.settings_btn.setIcon(QIcon(str(settings_icon_path)))
            self.settings_btn.setIconSize(QPixmap(str(settings_icon_path)).size())
        
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2D3748;
            }
            QPushButton:hover {
                color: #000000;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 17px;
            }
            QPushButton:pressed {
                color: #333333;
                background: rgba(0, 0, 0, 0.2);
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setToolTip("Настройки генерации")

        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        header_layout.addWidget(voice_label)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_btn)

        # Поле для ввода текста
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст, который нужно озвучить...")
        self.text_edit.setStyleSheet(AppStyles.get_text_edit_style())

        # Настройки генерации
        settings_layout = QVBoxLayout()

        # Чекбоксы на одной строке
        checkbox_layout = QHBoxLayout()

        self.play_checkbox = QCheckBox("Воспроизвести после генерации")
        self.play_checkbox.setChecked(True)
        self.play_checkbox.setStyleSheet(AppStyles.get_checkbox_style())

        self.save_checkbox = QCheckBox("Сохранить в файл")
        self.save_checkbox.setChecked(False)
        self.save_checkbox.setStyleSheet(AppStyles.get_checkbox_style())

        # Связываем чекбоксы
        self.play_checkbox.toggled.connect(self.on_play_toggled)
        self.save_checkbox.toggled.connect(self.on_save_toggled)

        checkbox_layout.addWidget(self.play_checkbox)
        checkbox_layout.addWidget(self.save_checkbox)
        checkbox_layout.addStretch()  # Добавляем растяжку для выравнивания

        # Поле для имени файла
        filename_layout = QHBoxLayout()

        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("Введите название для аудиофайла...")
        self.filename_edit.setStyleSheet(AppStyles.get_line_edit_style())
        self.filename_edit.setEnabled(False)

        filename_layout.addWidget(self.filename_edit, 1)

        settings_layout.addLayout(checkbox_layout)
        settings_layout.addLayout(filename_layout)

        # Прогресс-бар и кнопка генерации
        progress_layout = QVBoxLayout()

        # Метка статуса (скрыта, так как прогресс-бар будет показывать статус)
        self.status_label = QLabel("Готов к генерации")
        self.status_label.setVisible(False)


        # Прогресс-бар
        progress_bar_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(AppStyles.get_progress_bar_style())

        self.generate_btn = QPushButton("Начать генерацию")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet(AppStyles.get_button_style("primary"))
        self.generate_btn.clicked.connect(self.start_generation)

        progress_bar_layout.addWidget(self.progress_bar, 1)
        progress_bar_layout.addSpacing(10)
        progress_bar_layout.addWidget(self.generate_btn)

        progress_layout.addLayout(progress_bar_layout)

        # Сборка интерфейса
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.text_edit, 1)
        main_layout.addLayout(settings_layout)
        main_layout.addLayout(progress_layout)

        central_widget.setLayout(main_layout)

    def on_play_toggled(self, checked):
        """Обработка переключения чекбокса воспроизведения"""
        if not checked and not self.save_checkbox.isChecked():
            self.save_checkbox.setChecked(True)

    def on_save_toggled(self, checked):
        """Обработка переключения чекбокса сохранения"""
        self.filename_edit.setEnabled(checked)
        if not checked and not self.play_checkbox.isChecked():
            self.play_checkbox.setChecked(True)

    def start_generation(self):
        """Начало генерации речи"""
        text = self.text_edit.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для генерации!")
            return

        if self.save_checkbox.isChecked() and not self.filename_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название файла!")
            return

        # Получаем настройки
        play_after = self.play_checkbox.isChecked()
        save_file = self.save_checkbox.isChecked()
        filename = self.filename_edit.text().strip() if save_file else ""

        # Блокируем интерфейс
        self.generate_btn.setEnabled(False)
        self.back_btn.setEnabled(False)
        self.text_edit.setEnabled(False)
        self.play_checkbox.setEnabled(False)
        self.save_checkbox.setEnabled(False)
        self.filename_edit.setEnabled(False)

        # Показываем прогресс-бар и сбрасываем стиль
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Подготовка...")
        # Сбрасываем стиль к обычному
        self.progress_bar.setStyleSheet(AppStyles.get_progress_bar_style())

        # Подключаем перехват консольного вывода
        self._connect_console_signals()

        # Запускаем поток генерации
        self.generation_thread = GenerationWorker(
            text, self.voice_path, play_after, save_file, filename, self.device, self.language
        )
        self.generation_thread.progress_updated.connect(self.on_progress_updated)
        self.generation_thread.generation_finished.connect(self.on_generation_finished)
        self.generation_thread.start()

    def on_progress_updated(self, value, message):
        """Обновление прогресса генерации"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message} ({value}%)")

    def on_console_progress(self, percentage, message):
        """Обработка прогресса из консоли"""
        # Конвертируем проценты: 100% загрузки файлов = 25% общего прогресса
        if "Загрузка файлов" in message:
            ui_percentage = int(percentage * 0.25)  # 0-25%
        elif "Генерация речи" in message:
            ui_percentage = 25 + int(percentage * 0.6)  # 25-85%
        else:
            ui_percentage = percentage
            
        self.progress_bar.setValue(ui_percentage)
        self.progress_bar.setFormat(f"{message} ({ui_percentage}%)")
        self.current_progress = ui_percentage

    def on_generation_complete(self):
        """Обработка завершения генерации - начинаем плавное увеличение до 100%"""
        # Устанавливаем прогресс на 80%
        self.current_progress = 80
        self.progress_bar.setValue(80)
        self.progress_bar.setFormat("Подготовка к воспроизведению... (80%)")
        
        # Запускаем таймер для плавного увеличения
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.increment_progress)
        self.progress_timer.start(2000)  # Каждые 2 секунды

    def increment_progress(self):
        """Плавное увеличение прогресса каждые 2 секунды"""
        if self.current_progress < 100:
            self.current_progress += 1
            self.progress_bar.setValue(self.current_progress)
            self.progress_bar.setFormat(f"Подготовка к воспроизведению... ({self.current_progress}%)")
        else:
            # Останавливаем таймер когда достигли 100%
            if self.progress_timer:
                self.progress_timer.stop()
                self.progress_timer = None

    def on_generation_finished(self, success, message, file_path):
        """Завершение генерации"""
        # Отключаем перехват консольного вывода
        self._disconnect_console_signals()
        
        # Останавливаем таймер если он работает
        if self.progress_timer:
            self.progress_timer.stop()
            self.progress_timer = None
        
        # Разблокируем интерфейс
        self.generate_btn.setEnabled(True)
        self.back_btn.setEnabled(True)
        self.text_edit.setEnabled(True)
        self.play_checkbox.setEnabled(True)
        self.save_checkbox.setEnabled(True)
        self.filename_edit.setEnabled(self.save_checkbox.isChecked())

        if success:
            # Зеленый прогресс-бар с текстом "Готово"
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Готово")
            self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLES['success'])
            
            # Показываем кастомный диалог с кнопкой "Открыть папку"
            dialog = SuccessDialog(self, message, file_path)
            dialog.exec()
        else:
            # Красный прогресс-бар при ошибке
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Ошибка")
            self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLES['error'])
            QMessageBox.critical(self, "Ошибка", message)

    def open_settings(self):
        """Открытие окна настроек"""
        dialog = SettingsDialog(self)
        
        # Устанавливаем текущие значения из главного окна
        if self.device == "cuda":
            dialog.device_index = 0
        else:
            dialog.device_index = 1
        
        if self.language == "ru":
            dialog.language_index = 0
        else:
            dialog.language_index = 1
        
        dialog.update_device_tabs()
        dialog.language_combo.setCurrentIndex(dialog.language_index)
        
        # Показываем диалог
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Сохраняем новые настройки
            self.device = dialog.get_device()
            self.language = dialog.get_language()
            
            # Показываем уведомление об изменении настроек
            QMessageBox.information(
                self, 
                "Настройки сохранены", 
                f"Устройство: {self.device.upper()}\nЯзык: {self.language.upper()}"
            )

    def go_back(self):
        """Возврат к менеджеру голосов"""
        if self.generation_thread and self.generation_thread.isRunning():
            reply = QMessageBox.question(
                self,
                'Подтверждение',
                'Генерация еще выполняется. Вы уверены, что хотите прервать процесс и вернуться?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            self.generation_thread.stop()
            self.generation_thread.wait(1000)  # Ждем до 1 секунды для завершения

        # Импортируем здесь, чтобы избежать циклического импорта
        from voice_manager import VoiceManagerWindow

        # Создаем и показываем окно менеджера голосов
        self.voice_manager = VoiceManagerWindow()
        self.voice_manager.show()

        # Закрываем текущее окно
        self.close()


class SuccessDialog(QDialog):
    """Диалог успешной генерации с кнопкой открытия папки"""
    
    def __init__(self, parent, message, file_path=""):
        super().__init__(parent)
        self.file_path = file_path
        self.setup_ui(message)
    
    def setup_ui(self, message):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Успех")
        self.setModal(True)
        self.resize(400, 150)
        
        layout = QVBoxLayout()
        
        # Сообщение
        message_label = QLabel(f"Генерация завершена!\n{message}")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        # Кнопка "Открыть папку" (только если файл был сохранен)
        if self.file_path:
            open_folder_btn = QPushButton("📁 Открыть папку")
            open_folder_btn.clicked.connect(self.open_folder)
            button_layout.addWidget(open_folder_btn)
        
        # Кнопка "OK"
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def open_folder(self):
        """Открыть папку с файлом"""
        if self.file_path:
            import os
            import subprocess
            import platform
            
            folder_path = os.path.dirname(self.file_path)
            
            try:
                if platform.system() == "Windows":
                    os.startfile(folder_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть папку: {str(e)}")
        
        self.accept()

