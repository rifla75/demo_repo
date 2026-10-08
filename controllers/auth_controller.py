"""Управление авторизацией."""
from models.user import find_by_login

_current_user = None


def login(login_name):
    global _current_user
    user = find_by_login(login_name.strip())
    if user is None:
        return False, 'Пользователь с таким логином не найден'
    _current_user = user
    return True, user


def logout():
    global _current_user
    _current_user = None


def current_user():
    return _current_user