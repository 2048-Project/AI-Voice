import sys
import shutil
import subprocess
from pathlib import Path
import tempfile

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QScrollArea, QLabel, QPushButton,
                             QGridLayout, QMessageBox, QFrame, QFileDialog,
                             QProgressDialog, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from audio_utils import get_audio_duration, calculate_voice_accuracy, get_voice_accuracy_info
from styles import AppStyles

# Константы для оптимизации
VOICE_CARD_SIZE = (200, 140)
ICON_SIZE = 32
BUTTON_SIZE = 40



class AudioImportThread(QThread):
    progress_updated = pyqtSignal(int)
    import_finished = pyqtSignal(str, float, float, str)
    import_failed = pyqtSignal(str)

    def __init__(self, file_path, voices_dir, voice_name):
        super().__init__()
        self.file_path = file_path
        self.voices_dir = voices_dir
        self.voice_name = voice_name
        self.optimal_duration = 15.0

    def run(self):
        self.progress_updated.emit(10)
        output_path = self.convert_to_wav(self.file_path)
        
        self.progress_updated.emit(30)
        duration = self.get_audio_duration(output_path)
        
        if duration == 0:
            self.import_failed.emit("Не удалось определить длительность аудио после конвертации")
            return

        self.progress_updated.emit(50)
        accuracy, accuracy_text = self.calculate_accuracy(duration)
        
        self.progress_updated.emit(80)
        final_path = self.copy_to_voices(output_path)
        
        self.progress_updated.emit(100)
        self.import_finished.emit(final_path.name, duration, accuracy, accuracy_text)

    def get_audio_duration(self, file_path):
        return get_audio_duration(file_path)

    def calculate_accuracy(self, duration):
        return calculate_voice_accuracy(duration, self.optimal_duration)

    def convert_to_wav(self, input_path):
        input_path = Path(input_path)

        if input_path.suffix.lower() == '.wav':
            return input_path

        temp_dir = tempfile.gettempdir()
        output_path = Path(temp_dir) / f"converted_{self.voice_name}.wav"

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-ac', '1', '-ar', '24000', '-acodec', 'pcm_s16le', '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        return output_path

    def copy_to_voices(self, source_path):
        source_path = Path(source_path)
        target_path = self.voices_dir / f"{self.voice_name}.wav"

        counter = 1
        original_name = self.voice_name
        while target_path.exists():
            target_path = self.voices_dir / f"{original_name}_{counter}.wav"
            counter += 1

        shutil.copy2(source_path, target_path)
        return target_path


class VoiceCard(QFrame):
    def __init__(self, voice_file, index, accuracy=100.0, accuracy_text="100%"):
        super().__init__()
        self.voice_file = voice_file
        self.index = index
        self.accuracy = accuracy
        self.accuracy_text = accuracy_text
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(*VOICE_CARD_SIZE)

        colors = AppStyles.get_voice_card_colors(self.accuracy)
        self.setStyleSheet(AppStyles.get_voice_card_style(colors))

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Верхняя панель с номером и кнопкой удаления
        top_layout = QHBoxLayout()

        icon_label = QLabel(str(self.index + 1))
        icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        icon_label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            color: #2D3748;
            font-size: 14px;
            font-weight: bold;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка удаления (чёрный крестик)
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(ICON_SIZE, ICON_SIZE)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2D3748;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #E53E3E;
            }
        """)
        delete_btn.clicked.connect(self.delete_voice)

        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        top_layout.addWidget(delete_btn)

        # Название файла
        name_label = QLabel(self.voice_file.stem)
        name_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)

        # Информация о файле
        file_size = self.voice_file.stat().st_size / 1024
        duration = get_audio_duration(self.voice_file)
        info_text = f"{file_size:.1f} KB | {duration:.1f} сек"

        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #E2E8F0; font-size: 11px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Точность голоса
        accuracy_type = "Точность" if self.accuracy <= 100 else "Превышение"
        accuracy_label = QLabel(f"{accuracy_type}: {self.accuracy_text}")
        accuracy_label.setStyleSheet("""
            color: #FFFFFF; font-size: 12px; font-weight: bold; 
            background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 2px 6px;
        """)
        accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(top_layout)
        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addWidget(accuracy_label)

        self.setLayout(layout)


    def delete_voice(self):
        """Удаление голоса с подтверждением на русском"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f'Вы уверены, что хотите удалить голос "{self.voice_file.stem}"?')
        msg_box.setIcon(QMessageBox.Icon.Question)

        # Создаем кастомные кнопки на русском
        yes_button = msg_box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(no_button)

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            # Удаляем файл
            self.voice_file.unlink()
            # Удаляем карточку из интерфейса
            self.setParent(None)
            self.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Закрываем текущее окно и открываем окно генерации
            parent_window = self.window()
            if hasattr(parent_window, 'start_generation'):
                parent_window.start_generation(self.voice_file)


class VoiceManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.voices_dir = Path("voices")
        self.setup_ui()
        self.load_voices()

    def setup_ui(self):
        self.setWindowTitle("Менеджер голосов")
        self.setMinimumSize(1000, 700)
        
        # Установка иконки окна
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхний бар с выделенным фоном
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: #EDF2F7;
            border-bottom: 1px solid #CBD5E0;
        """)
        header_widget.setFixedHeight(70)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Кнопка добавления (чёрный плюс на белом фоне)
        add_btn = QPushButton("+")
        add_btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2D3748;
                font-size: 24px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #38A169;
            }
            QPushButton:pressed {
                color: #2F855A;
            }
        """)
        add_btn.clicked.connect(self.import_voice)
        add_btn.setToolTip("Добавить новый голос")

        # Название
        title_label = QLabel("Менеджер голосов")
        title_label.setStyleSheet("""
            color: #2D3748;
            font-size: 20px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка обновления (SVG иконка)
        refresh_btn = QPushButton()
        refresh_btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        
        # Загружаем SVG иконку
        reload_icon_path = Path("assets/reload.svg")
        if reload_icon_path.exists():
            refresh_btn.setIcon(QIcon(str(reload_icon_path)))
            refresh_btn.setIconSize(QPixmap(str(reload_icon_path)).size())
        
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2D3748;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #3182CE;
            }
            QPushButton:pressed {
                color: #2C5282;
            }
        """)
        refresh_btn.clicked.connect(self.load_voices)
        refresh_btn.setToolTip("Обновить список")

        header_layout.addWidget(add_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        header_widget.setLayout(header_layout)

        # Область с карточками
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: #F7FAFC; 
            }
            QScrollBar:vertical { 
                background: #EDF2F7; 
                width: 10px; 
                margin: 0px; 
            }
            QScrollBar::handle:vertical { 
                background: #CBD5E0; 
                border-radius: 5px; 
                min-height: 20px; 
            }
            QScrollBar::handle:vertical:hover { 
                background: #A0AEC0; 
            }
        """)

        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(20, 20, 20, 20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_widget.setLayout(self.cards_layout)

        scroll_area.setWidget(self.cards_widget)

        # Статус бар
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet("""
            color: #718096; 
            font-size: 11px; 
            padding: 3px 8px; 
            background: #EDF2F7; 
            border-radius: 3px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(20)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

    def import_voice(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите аудиофайл", "",
            "Аудиофайлы (*.mp3 *.wav *.ogg *.m4a *.flac *.aac);;Все файлы (*)"
        )

        if not file_path:
            return

        voice_name, ok = QInputDialog.getText(
            self, 'Название голоса', 'Введите название для этого голоса:',
            text=Path(file_path).stem
        )

        if not ok or not voice_name.strip():
            return

        voice_name = voice_name.strip()

        self.import_thread = AudioImportThread(file_path, self.voices_dir, voice_name)
        self.import_thread.progress_updated.connect(self.on_import_progress)
        self.import_thread.import_finished.connect(self.on_import_finished)
        self.import_thread.import_failed.connect(self.on_import_failed)

        self.progress_dialog = QProgressDialog("Импорт аудио...", "Отмена", 0, 100, self)
        self.progress_dialog.setWindowTitle("Импорт голоса")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.import_thread.terminate)
        self.progress_dialog.show()

        self.import_thread.start()

    def on_import_progress(self, value):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)

    def on_import_finished(self, filename, duration, accuracy, accuracy_text):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        accuracy_type = "Точность" if accuracy <= 100 else "Превышение"
        color = "#38A169" if accuracy >= 90 else "#D69E2E" if accuracy >= 70 else "#E53E3E"

        message = f"""
        <html>
        <b>Голос успешно импортирован!</b><br><br>
        Файл: <b>{filename}</b><br>
        Длительность: <b>{duration:.1f} сек</b><br>
        {accuracy_type}: <span style='color: {color};'><b>{accuracy_text}</b></span>
        </html>
        """

        QMessageBox.information(self, "Импорт завершен", message)
        self.load_voices()

    def on_import_failed(self, error_message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать аудио:\n{error_message}")

    def load_voices(self):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.voices_dir.mkdir(exist_ok=True)

        voice_files = list(self.voices_dir.glob("*.wav"))

        if not voice_files:
            self.show_empty_message()
            return

        for i, voice_file in enumerate(voice_files):
            accuracy, accuracy_text = self.calculate_voice_accuracy(voice_file)
            
            row, col = i // 4, i % 4
            voice_card = VoiceCard(voice_file, i, accuracy, accuracy_text)
            self.cards_layout.addWidget(voice_card, row, col)

        self.status_label.setText(f"Голосов: {len(voice_files)}")

    def calculate_voice_accuracy(self, voice_file):
        return get_voice_accuracy_info(voice_file)

    def show_empty_message(self):
        empty_label = QLabel("Пока что здесь пусто\n\nНажмите + чтобы добавить первый голос")
        empty_label.setStyleSheet("""
            color: #718096; 
            font-size: 16px; 
            padding: 60px; 
            background: #F7FAFC; 
            border: 2px dashed #CBD5E0; 
            border-radius: 12px;
        """)
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cards_layout.addWidget(empty_label, 0, 0, 1, 4)
        self.status_label.setText("Нет голосов")

    def start_generation(self, voice_file):
        """Запуск окна генерации с выбранным голосом"""
        # Показываем упрощенное окно загрузки
        from loading_screen import SimpleLoadingWindow, SimpleLoadingWorker
        
        self.loading_window = SimpleLoadingWindow()
        self.loading_window.show()
        
        # Скрываем основное окно
        self.hide()
        
        # Запускаем поток загрузки
        self.loading_worker = SimpleLoadingWorker()
        self.loading_worker.loading_finished.connect(self.on_loading_finished)
        self.loading_worker.start()
        
        # Сохраняем данные для передачи в окно генерации
        self.selected_voice_file = voice_file
        
    def on_loading_finished(self):
        """Завершение загрузки - открываем окно генерации"""
        try:
            # Импортируем здесь, чтобы избежать циклического импорта
            from generation_window import GenerationWindow

            # Создаем окно генерации
            self.generation_window = GenerationWindow(str(self.selected_voice_file), self.selected_voice_file.stem)
            self.generation_window.show()

            # Закрываем окно загрузки
            self.loading_window.close()
            
        except Exception as e:
            # В случае ошибки показываем сообщение и возвращаемся к менеджеру
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self.loading_window, "Ошибка", f"Не удалось загрузить программу: {str(e)}")
            self.loading_window.close()
            self.show()  # Показываем основное окно обратно