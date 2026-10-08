#"""Модуль подключения к PostgreSQL."""
import psycopg2
from psycopg2 import pool
import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'chudo_obuv'),
    'user': os.environ.get('DB_USER', 'obuv_user'),
    'password': os.environ.get('DB_PASSWORD', 'obuv_pass'),
}

_connection_pool = None


def init_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1, maxconn=5, **DB_CONFIG
        )
    return _connection_pool


def get_connection():
    if _connection_pool is None:
        init_pool()
    return _connection_pool.getconn()


def release_connection(conn):
    if _connection_pool is not None and conn is not None:
        _connection_pool.putconn(conn)


def close_all():
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None

