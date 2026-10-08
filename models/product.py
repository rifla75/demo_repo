
"""Работа с товарами."""
from db.connection import get_connection, release_connection


class Product:
    def __init__(self, product_id, product_name, category_name, manufacturer_name,
                 subcategory, image_path, description, composition, price,
                 total_quantity, base_price, final_price, discount_percent):
        self.product_id = product_id
        self.product_name = product_name
        self.category_name = category_name
        self.manufacturer_name = manufacturer_name
        self.subcategory = subcategory or ''
        self.image_path = image_path or ''
        self.description = description or ''
        self.composition = composition or ''
        self.price = base_price
        self.total_quantity = total_quantity
        self.base_price = base_price
        self.final_price = final_price
        self.discount_percent = discount_percent

    @property
    def availability(self):
        return 'много' if self.total_quantity > 5 else 'мало'

    @property
    def is_low_stock(self):
        return self.total_quantity <= 3



def list_products(category_id=None, search='', sort=''):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT (CURRENT_DATE - INTERVAL '1 month')::date,
                   (CURRENT_DATE)::date
        """)
        prev_start, prev_end = cur.fetchone()

        query = """
            SELECT p.product_id, p.product_name, c.category_name, m.manufacturer_name,
                   p.subcategory, p.image_path, p.description, p.composition, p.price,
                   COALESCE((SELECT SUM(quantity_available) FROM stock_items
                             WHERE product_id = p.product_id), 0) AS total_quantity,
                   (SELECT COUNT(*) FROM order_items oi
                       JOIN stock_items si ON si.stock_item_id = oi.stock_item_id
                       JOIN orders o ON o.order_id = oi.order_id
                       WHERE si.product_id = p.product_id
                         AND o.order_date >= %s AND o.order_date < %s)
            FROM products p
            JOIN categories c ON c.category_id = p.category_id
            JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
        """
        params = [prev_start, prev_end]
        where = []
        if category_id:
            where.append("c.category_id = %s")
            params.append(category_id)
        if search:
            where.append("(LOWER(p.product_name) LIKE %s OR LOWER(p.description) LIKE %s)")
            params.extend([f'%{search.lower()}%', f'%{search.lower()}%'])
        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        result = []
        for row in cur.fetchall():
            (pid, name, cat, man, subcat, image, descr, comp, price,
             total_qty, orders_last) = row
            discount = 25 if orders_last == 0 else 0
            final_price = round(float(price) * (100 - discount) / 100, 2)
            result.append(Product(pid, name, cat, man, subcat, image, descr, comp,
                                  float(price), int(total_qty), float(price),
                                  final_price, discount))
        if sort == 'price_asc':
            result.sort(key=lambda p: p.final_price)
        elif sort == 'price_desc':
            result.sort(key=lambda p: p.final_price, reverse=True)
        return result
    finally:
        release_connection(conn)




def get_product(product_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.product_id, p.product_name, c.category_name, m.manufacturer_name,
                   p.subcategory, p.image_path, p.description, p.composition, p.price,
                   COALESCE((SELECT SUM(quantity_available) FROM stock_items
                             WHERE product_id = p.product_id), 0),
                   (SELECT COUNT(*) FROM order_items oi
                       JOIN stock_items si ON si.stock_item_id = oi.stock_item_id
                       JOIN orders o ON o.order_id = oi.order_id
                       WHERE si.product_id = p.product_id
                         AND o.order_date >= (CURRENT_DATE - INTERVAL '1 month')::date
                         AND o.order_date < CURRENT_DATE)
            FROM products p
            JOIN categories c ON c.category_id = p.category_id
            JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
            WHERE p.product_id = %s
        """, (product_id,))
        row = cur.fetchone()
        if not row:
            return None
        (pid, name, cat, man, subcat, image, descr, comp, price, total_qty, orders_last) = row
        discount = 25 if orders_last == 0 else 0
        final_price = round(float(price) * (100 - discount) / 100, 2)
        return Product(pid, name, cat, man, subcat, image, descr, comp,
                       float(price), int(total_qty), float(price), final_price, discount)
    finally:
        release_connection(conn)


def get_sizes_for_product(product_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT si.stock_item_id, sz.size_value, si.quantity_available
            FROM stock_items si
            JOIN sizes sz ON sz.size_id = si.size_id
            WHERE si.product_id = %s
            ORDER BY CAST(sz.size_value AS NUMERIC)
        """, (product_id,))
        return cur.fetchall()
    finally:
        release_connection(conn)


def list_categories():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        return cur.fetchall()
    finally:
        release_connection(conn)


def search_products(query, limit=20):
    """Поиск товаров для формы ручного создания заказа."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.product_id, p.product_name, m.manufacturer_name, p.price
            FROM products p
            JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
            WHERE LOWER(p.product_name) LIKE %s
            ORDER BY p.product_name
            LIMIT %s
        """, (f'%{query.lower()}%', limit))
        return cur.fetchall()
    finally:
        release_connection(conn)