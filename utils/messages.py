"""Диалоги сообщений."""
from PyQt5.QtWidgets import QMessageBox


def show_info(parent, text, title='Информация'):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.exec_()


def show_warning(parent, text, title='Предупреждение'):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    box.exec_()


def show_error(parent, text, title='Ошибка'):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.exec_()


def ask_confirmation(parent, text, title='Подтверждение'):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    return box.exec_() == QMessageBox.Yes