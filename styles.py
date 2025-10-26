"""
Общие стили для приложения
"""
from PyQt6.QtWidgets import QPushButton, QCheckBox, QLineEdit, QTextEdit, QProgressBar


class AppStyles:
    """Класс с общими стилями для приложения"""
    
    # Цветовая палитра
    COLORS = {
        'primary': '#2D3748',
        'secondary': '#4A5568', 
        'success': '#48BB78',
        'success_hover': '#38A169',
        'warning': '#ED8936',
        'error': '#FC8181',
        'background': '#F7FAFC',
        'surface': '#EDF2F7',
        'border': '#CBD5E0',
        'text_primary': '#2D3748',
        'text_secondary': '#718096',
        'white': '#FFFFFF'
    }
    
    @staticmethod
    def get_button_style(style_type="primary"):
        """Стили для кнопок"""
        styles = {
            "primary": f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {AppStyles.COLORS['success']}, stop:1 {AppStyles.COLORS['success_hover']});
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #58CB88, stop:1 #48B179);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #38A168, stop:1 #289159);
                }}
                QPushButton:disabled {{
                    background: #A0AEC0;
                    color: #E2E8F0;
                }}
            """,
            "secondary": f"""
                QPushButton {{
                    background: {AppStyles.COLORS['white']};
                    color: {AppStyles.COLORS['primary']};
                    border: 1px solid {AppStyles.COLORS['border']};
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {AppStyles.COLORS['background']};
                    border: 1px solid #A0AEC0;
                }}
                QPushButton:disabled {{
                    background: #A0AEC0;
                }}
            """,
            "back": f"""
                QPushButton {{
                    background: {AppStyles.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {AppStyles.COLORS['secondary']};
                }}
                QPushButton:disabled {{
                    background: #A0AEC0;
                }}
            """,
            "icon": f"""
                QPushButton {{
                    background: {AppStyles.COLORS['white']};
                    border: 1px solid {AppStyles.COLORS['border']};
                    border-radius: 20px;
                    color: {AppStyles.COLORS['primary']};
                    font-size: 24px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }}
                QPushButton:hover {{
                    background: {AppStyles.COLORS['background']};
                    border: 1px solid #A0AEC0;
                }}
                QPushButton:pressed {{
                    background: {AppStyles.COLORS['surface']};
                }}
            """
        }
        return styles.get(style_type, styles["primary"])
    
    @staticmethod
    def get_text_edit_style():
        """Стиль для текстовых полей"""
        return f"""
            QTextEdit {{
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-height: 120px;
            }}
            QTextEdit:focus {{
                border: 2px solid #4299E1;
            }}
        """
    
    @staticmethod
    def get_line_edit_style():
        """Стиль для полей ввода"""
        return f"""
            QLineEdit {{
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid #4299E1;
            }}
            QLineEdit:disabled {{
                background: {AppStyles.COLORS['surface']};
                color: #A0AEC0;
            }}
        """
    
    @staticmethod
    def get_checkbox_style():
        """Стиль для чекбоксов"""
        return f"""
            QCheckBox {{
                color: {AppStyles.COLORS['primary']};
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {AppStyles.COLORS['border']};
                border-radius: 3px;
                background: {AppStyles.COLORS['white']};
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid #4299E1;
                border-radius: 3px;
                background: #4299E1;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
        """
    
    @staticmethod
    def get_progress_bar_style():
        """Стиль для прогресс-бара"""
        return f"""
            QProgressBar {{
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: 5px;
                text-align: center;
                background: {AppStyles.COLORS['surface']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4299E1, stop:1 #3182CE);
                border-radius: 4px;
            }}
        """
    
    @staticmethod
    def get_voice_card_colors(accuracy):
        """Цвета для карточек голосов в зависимости от точности"""
        if accuracy >= 90:
            return ("#48BB78", "#38A169", "#68D391")
        elif accuracy >= 70:
            return ("#ED8936", "#DD6B20", "#F6AD55")
        else:
            return ("#FC8181", "#E53E3E", "#FEB2B2")
    
    @staticmethod
    def get_voice_card_style(colors):
        """Стиль для карточек голосов"""
        return f"""
            VoiceCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors[0]}, stop:1 {colors[1]});
                border-radius: 12px;
                border: 2px solid {colors[2]};
            }}
            VoiceCard:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors[2]}, stop:1 {colors[0]});
                border: 2px solid #FFFFFF;
            }}
        """
