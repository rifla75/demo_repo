"""Импорт данных из xlsx в PostgreSQL."""
import os
import sys
import openpyxl

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import get_connection, release_connection

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
)


def read_xlsx(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f'[!] Файл не найден: {path}, пропускаем.')
        return []
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    return rows[1:]


def get_or_create(cur, table, id_col, name_col, name):
    name = (name or '').strip()
    cur.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} ({name_col}) VALUES (%s) RETURNING {id_col}", (name,))
    return cur.fetchone()[0]


def import_roles(cur):
    for r in ['Администратор', 'Менеджер', 'Авторизованный пользователь']:
        cur.execute("INSERT INTO roles (role_name) VALUES (%s) ON CONFLICT DO NOTHING", (r,))


def import_users(cur):
    for row in read_xlsx('Users_import.xlsx'):
        if len(row) < 5 or not row[3]:
            continue
        cur.execute("SELECT role_id FROM roles WHERE role_name = %s", (row[4],))
        r = cur.fetchone()
        if not r:
            continue
        cur.execute("""
            INSERT INTO users (last_name, first_name, middle_name, login, role_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (login) DO NOTHING
        """, (row[0], row[1], row[2], row[3], r[0]))


def import_sizes(cur):
    for row in read_xlsx('Sizes_import.xlsx'):
        if row and row[0] is not None:
            cur.execute("INSERT INTO sizes (size_value) VALUES (%s) ON CONFLICT DO NOTHING",
                        (str(row[0]).strip(),))


def import_products(cur):
    for row in read_xlsx('Products_import.xlsx'):
        if len(row) < 8 or not row[3]:
            continue
        cat_id = get_or_create(cur, 'categories', 'category_id', 'category_name', row[0])
        man_id = get_or_create(cur, 'manufacturers', 'manufacturer_id', 'manufacturer_name', row[4])
        cur.execute("""
            INSERT INTO products (category_id, manufacturer_id, subcategory,
                product_name, image_path, description, composition, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_name, manufacturer_id) DO UPDATE
                SET price = EXCLUDED.price
        """, (cat_id, man_id, row[1], row[3], row[2], row[5], row[6], float(row[7])))


def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        import_roles(cur)
        import_users(cur)
        import_sizes(cur)
        import_products(cur)
        conn.commit()
        print('[OK] Импорт завершён (или пропущен, если файлов нет).')
    except Exception as e:
        conn.rollback()
        print(f'[ОШИБКА] {e}')
    finally:
        cur.close()
        release_connection(conn)


if __name__ == '__main__':
    main()

