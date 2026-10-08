"""Окно авторизации."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon

from controllers import auth_controller
from utils import messages


class LoginWindow(QWidget):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Чудо Обувь — Вход в систему')
        self.setWindowIcon(QIcon('resources/images/icon.png'))
        self.setFixedSize(420, 320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        logo = QLabel()
        pix = QPixmap('resources/images/logo.png')
        if not pix.isNull():
            logo.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio,
                                       Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel('Чудо Обувь')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 22px; font-weight: bold; color: #2c3e50;')
        layout.addWidget(title)

        subtitle = QLabel('Вход в систему (пароль не требуется)')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #666; margin-bottom: 10px;')
        layout.addWidget(subtitle)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Введите логин, например isivanov')
        self.login_input.setStyleSheet('padding: 8px; font-size: 14px;')
        self.login_input.returnPressed.connect(self._on_login)
        layout.addWidget(self.login_input)

        btns = QHBoxLayout()
        btns.addStretch()
        self.login_btn = QPushButton('Войти')
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 8px 24px; border: none; border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.login_btn.clicked.connect(self._on_login)
        btns.addWidget(self.login_btn)
        layout.addLayout(btns)

        hint = QLabel('Логины: isivanov, papetrov, asidorova, ...')
        hint.setStyleSheet('color: #888; font-size: 11px; margin-top: 10px;')
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        self.setLayout(layout)

    def _on_login(self):
        login = self.login_input.text().strip()
        if not login:
            messages.show_warning(self, 'Введите логин')
            return
        ok, result = auth_controller.login(login)
        if not ok:
            messages.show_error(self, result)
            return
        self.login_success.emit()