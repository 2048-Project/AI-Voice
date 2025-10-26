import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from styles import AppStyles

# Создание директорий
Path("voices").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

app = QApplication(sys.argv)
app.setStyleSheet(f"QMainWindow {{ background: {AppStyles.COLORS['background']}; }}")

# Установка иконки приложения
icon_path = Path("assets/icon.ico")
if icon_path.exists():
    app.setWindowIcon(QIcon(str(icon_path)))

# Сразу открываем основное окно без анимации
from voice_manager import VoiceManagerWindow
window = VoiceManagerWindow()
window.show()

sys.exit(app.exec())