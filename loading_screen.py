import sys, time, math
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRectF, QSize, QPointF
from PyQt6.QtGui import QMovie, QPainter, QPaintEvent, QColor, QPen, QBrush


class SimpleSpinner(QWidget):
    """Простой анимированный спиннер"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # Обновление каждые 30мс
        
    def update_animation(self):
        self.angle = (self.angle + 12) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем круговой прогресс
        rect = self.rect().adjusted(10, 10, -10, -10)
        
        # Фон круга
        painter.setPen(QPen(Qt.GlobalColor.lightGray, 6))
        painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawEllipse(rect)
        
        # Анимированная дуга
        painter.setPen(QPen(Qt.GlobalColor.blue, 6))
        painter.drawArc(rect, self.angle * 16, 300 * 16)  # 300 градусов дуги
        
        # Добавляем точку на конце дуги
        center = QPointF(40, 40)
        radius = 30
        end_angle_rad = math.radians(self.angle + 300)
        end_x = center.x() + radius * math.cos(end_angle_rad)
        end_y = center.y() + radius * math.sin(end_angle_rad)
        
        painter.setPen(QPen(Qt.GlobalColor.darkBlue, 8))
        painter.drawPoint(int(end_x), int(end_y))


class SimpleLoadingWindow(QWidget):
    """Улучшенное окно загрузки с GIF анимацией"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = time.time()
        self.setWindowTitle("Загрузка...")
        self.setFixedSize(400, 200)
        # Безрамочное окно
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Важно: включаем "translucent background" — это не делает фон полупрозрачным само по себе,
        # но позволяет иметь прозрачные уголки окна. Фон мы будем рисовать полностью непрозрачным.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(1)  # уменьшенное расстояние

        self.loading_gif = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.loading_gif.setFixedSize(100, 100)
        gif_path = Path("assets/loading.gif")
        if gif_path.exists():
            movie = QMovie(str(gif_path))
            movie.setScaledSize(QSize(100, 100))
            movie.setSpeed(75)
            self.loading_gif.setMovie(movie)
            movie.start()
        else:
            self.loading_gif.setText("Загрузка...")

        self.timer_label = QLabel("Загрузка... (0.0 сек)", alignment=Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(self.loading_gif, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)
        self.setLayout(layout)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(50)

        self.center_window()

    def paintEvent(self, event: QPaintEvent):
        # Рисуем полностью непрозрачный белый фон с закруглёнными углами.
        radius = 15.0
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 255))  # alpha = 255 => непрозрачный
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        painter.end()

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_display(self):
        elapsed = time.time() - self.start_time
        seconds = int(elapsed)
        milliseconds = int((elapsed - seconds) * 100)
        self.timer_label.setText(f"Загрузка... ({seconds}.{milliseconds:02d} сек)")
        
    def close_loading(self):
        """Закрытие окна загрузки"""
        self.close()


class SimpleLoadingWorker(QThread):
    """Поток для загрузки библиотек"""
    
    loading_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        try:
            # Импорт основных библиотек
            import os
            import sys
            import time
            
            # Импорт PyQt6
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            
            # Импорт torch
            import torch
            
            # Импорт numpy
            import numpy as np
            
            # Импорт chatterbox
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            
            self.loading_finished.emit()
            
        except Exception as e:
            self.loading_finished.emit()


