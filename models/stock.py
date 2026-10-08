"""Работа со складом."""
from db.connection import get_connection, release_connection


def get_stock_item(stock_item_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT si.stock_item_id, si.product_id, si.size_id, si.quantity_available,
                   p.product_name, p.price, m.manufacturer_name, sz.size_value
            FROM stock_items si
            JOIN products p ON p.product_id = si.product_id
            JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
            JOIN sizes sz ON sz.size_id = si.size_id
            WHERE si.stock_item_id = %s
        """, (stock_item_id,))
        return cur.fetchone()
    finally:
        release_connection(conn)


def decrease_quantity(cur, stock_item_id, amount):
    cur.execute("""
        UPDATE stock_items
        SET quantity_available = quantity_available - %s
        WHERE stock_item_id = %s AND quantity_available >= %s
        RETURNING quantity_available
    """, (amount, stock_item_id, amount))
    if cur.fetchone() is None:
        raise ValueError('Недостаточно товара на складе')


def increase_quantity(cur, stock_item_id, amount):
    cur.execute("""
        UPDATE stock_items
        SET quantity_available = quantity_available + %s
        WHERE stock_item_id = %s
    """, (amount, stock_item_id))
