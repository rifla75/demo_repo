"""
Точка входа в приложение «Чудо Обувь».
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from db.connection import init_pool, close_all
from views.login_window import LoginWindow
from views.main_window import MainWindow
from utils import messages


def load_styles(app):
    path = 'resources/styles/style.qss'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Чудо Обувь')
    app.setWindowIcon(QIcon('resources/images/icon.png'))
    load_styles(app)

    try:
        init_pool()
    except Exception as e:
        messages.show_error(None, f'Не удалось подключиться к базе данных:\n{e}')
        sys.exit(1)

    login_window = LoginWindow()
    main_window_ref = {'window': None}

    def on_login_success():
        window = MainWindow()
        main_window_ref['window'] = window
        window.show()
        login_window.close()

    login_window.login_success.connect(on_login_success)
    login_window.show()

    exit_code = app.exec_()
    close_all()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()