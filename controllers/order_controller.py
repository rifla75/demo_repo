"""Логика заказов."""
from models.order import (list_orders, get_order, create_order,
                          delete_order, update_order, create_order_manual)


def get_all_orders():
    return list_orders()


def get_user_orders(user_id):
    return list_orders(user_id=user_id)


def get_order_details(order_id):
    return get_order(order_id)


def place_order(user_id, items):
    if not items:
        raise ValueError('Заказ пуст')
    return create_order(user_id, items)


def place_manual_order(user_id, order_date, items):
    if not items:
        raise ValueError('Заказ пуст')
    return create_order_manual(user_id, order_date, items)


def remove_order(order_id):
    delete_order(order_id)


def edit_order(order_id, new_date, remove_item_ids):
    update_order(order_id, new_date, remove_item_ids)