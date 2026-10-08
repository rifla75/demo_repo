"""Расчёт скидки 25%."""
from datetime import datetime, timedelta
from db.connection import get_connection, release_connection


def get_previous_month_range():
    today = datetime.now().date()
    first_of_current = today.replace(day=1)
    last_of_prev = first_of_current - timedelta(days=1)
    first_of_prev = last_of_prev.replace(day=1)
    return first_of_prev, first_of_current


def has_orders_last_month(product_id):
    start, end = get_previous_month_range()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM order_items oi
            JOIN stock_items si ON si.stock_item_id = oi.stock_item_id
            JOIN orders o ON o.order_id = oi.order_id
            WHERE si.product_id = %s
              AND o.order_date >= %s
              AND o.order_date < %s
        """, (product_id, start, end))
        return cur.fetchone()[0] > 0
    finally:
        release_connection(conn)


def calculate_final_price(product_id, base_price):
    if has_orders_last_month(product_id):
        return float(base_price), 0
    return round(float(base_price) * 0.75, 2), 25