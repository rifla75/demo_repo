"""Валидация ввода."""


def is_positive_int(value):
    try:
        n = int(value)
        return n > 0
    except (TypeError, ValueError):
        return False


def validate_quantity(value, max_available):
    if not value:
        return False, 'Введите количество'
    try:
        n = int(value)
    except ValueError:
        return False, 'Количество должно быть целым числом'
    if n <= 0:
        return False, 'Количество должно быть положительным'
    if n > max_available:
        return False, f'Доступно не более {max_available} шт.'
    return True, ''