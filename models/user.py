"""Работа с пользователями."""
from db.connection import get_connection, release_connection


class User:
    def __init__(self, user_id, last_name, first_name, middle_name, login, role_name):
        self.user_id = user_id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name or ''
        self.login = login
        self.role_name = role_name

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()

    @property
    def is_admin(self):
        return self.role_name == 'Администратор'

    @property
    def is_manager(self):
        return self.role_name == 'Менеджер'

    @property
    def can_manage_orders(self):
        return self.role_name in ('Администратор', 'Менеджер')


def find_by_login(login):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.last_name, u.first_name, u.middle_name, u.login, r.role_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            WHERE u.login = %s
        """, (login,))
        row = cur.fetchone()
        return User(*row) if row else None
    finally:
        release_connection(conn)


def list_all():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.last_name, u.first_name, u.middle_name, u.login, r.role_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            ORDER BY u.last_name
        """)
        return [User(*row) for row in cur.fetchall()]
    finally:
        release_connection(conn)