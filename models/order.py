"""Работа с заказами."""
from db.connection import get_connection, release_connection
from models import stock as stock_model


class Order:
    def __init__(self, order_id, order_date, user_id, fio):
        self.order_id = order_id
        self.order_date = order_date
        self.user_id = user_id
        self.fio = fio


def list_orders(user_id=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if user_id:
            cur.execute("""
                SELECT o.order_id, o.order_date, o.user_id,
                       u.last_name || ' ' || u.first_name || ' ' || COALESCE(u.middle_name, '')
                FROM orders o
                JOIN users u ON u.user_id = o.user_id
                WHERE o.user_id = %s
                ORDER BY o.order_id DESC
            """, (user_id,))
        else:
            cur.execute("""
                SELECT o.order_id, o.order_date, o.user_id,
                       u.last_name || ' ' || u.first_name || ' ' || COALESCE(u.middle_name, '')
                FROM orders o
                JOIN users u ON u.user_id = o.user_id
                ORDER BY o.order_id DESC
            """)
        return [Order(*row) for row in cur.fetchall()]
    finally:
        release_connection(conn)


def get_order(order_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT o.order_id, o.order_date, o.user_id,
                   u.last_name || ' ' || u.first_name || ' ' || COALESCE(u.middle_name, '')
            FROM orders o
            JOIN users u ON u.user_id = o.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        row = cur.fetchone()
        if not row:
            return None
        order = Order(*row)
        cur.execute("""
            SELECT oi.order_item_id, oi.quantity, oi.price,
                   p.product_name, m.manufacturer_name, sz.size_value
            FROM order_items oi
            JOIN stock_items si ON si.stock_item_id = oi.stock_item_id
            JOIN products p ON p.product_id = si.product_id
            JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
            JOIN sizes sz ON sz.size_id = si.size_id
            WHERE oi.order_id = %s
            ORDER BY oi.order_item_id
        """, (order_id,))
        order.items = cur.fetchall()
        order.total = sum(it[1] * float(it[2]) for it in order.items)
        return order
    finally:
        release_connection(conn)


def create_order(user_id, items):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (order_date, user_id)
            VALUES (CURRENT_DATE, %s) RETURNING order_id
        """, (user_id,))
        order_id = cur.fetchone()[0]
        for item in items:
            stock_id = item['stock_item_id']
            qty = item['quantity']
            stock_model.decrease_quantity(cur, stock_id, qty)
            cur.execute("""
                SELECT p.price FROM stock_items si
                JOIN products p ON p.product_id = si.product_id
                WHERE si.stock_item_id = %s
            """, (stock_id,))
            price = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO order_items (order_id, stock_item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, stock_id, qty, price))
        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


def create_order_manual(user_id, order_date, items):
    """Ручное создание заказа (Менеджер/Администратор)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (order_date, user_id)
            VALUES (%s, %s) RETURNING order_id
        """, (order_date, user_id))
        order_id = cur.fetchone()[0]
        for item in items:
            stock_id = item['stock_item_id']
            qty = item['quantity']
            price = item['price']
            stock_model.decrease_quantity(cur, stock_id, qty)
            cur.execute("""
                INSERT INTO order_items (order_id, stock_item_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, stock_id, qty, price))
        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


def delete_order(order_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT stock_item_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
        for stock_id, qty in cur.fetchall():
            stock_model.increase_quantity(cur, stock_id, qty)
        cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


def update_order(order_id, new_date, remove_item_ids):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if new_date:
            cur.execute("UPDATE orders SET order_date = %s WHERE order_id = %s",
                        (new_date, order_id))
        for item_id in remove_item_ids:
            cur.execute("SELECT stock_item_id, quantity FROM order_items WHERE order_item_id = %s",
                        (item_id,))
            row = cur.fetchone()
            if row:
                stock_model.increase_quantity(cur, row[0], row[1])
                cur.execute("DELETE FROM order_items WHERE order_item_id = %s", (item_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)