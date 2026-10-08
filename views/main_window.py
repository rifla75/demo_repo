"""Главное окно приложения."""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget)
from PyQt5.QtGui import QIcon

from controllers.auth_controller import current_user, logout
from controllers import order_controller
from views.catalog_view import CatalogView
from views.product_view import ProductView
from views.cart_view import CartView
from views.orders_view import OrdersView
from views.order_edit_view import OrderEditView
from utils import messages


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Чудо Обувь — Система оформления заказов')
        self.setWindowIcon(QIcon('resources/images/icon.png'))
        self.resize(1100, 720)

        self.cart = []

        self._build_ui()
        self._refresh_header()
        self.catalog_view.reload()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Шапка
        self.header = QWidget()
        self.header.setStyleSheet('background-color: #2c3e50;')
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 10, 16, 10)

        logo = QLabel('👟 Чудо Обувь')
        logo.setStyleSheet('color: white; font-size: 18px; font-weight: bold;')
        header_layout.addWidget(logo)
        header_layout.addStretch()

        self.user_label = QLabel('')
        self.user_label.setStyleSheet('color: white; font-size: 13px;')
        header_layout.addWidget(self.user_label)

        self.catalog_btn = QPushButton('Каталог')
        self.catalog_btn.setStyleSheet(self._header_btn_style())
        self.catalog_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header_layout.addWidget(self.catalog_btn)

        self.cart_btn = QPushButton('🛒 Корзина (0)')
        self.cart_btn.setStyleSheet(self._header_btn_style())
        self.cart_btn.clicked.connect(self._open_cart)
        header_layout.addWidget(self.cart_btn)

        self.orders_btn = QPushButton('📋 Заказы')
        self.orders_btn.setStyleSheet(self._header_btn_style())
        self.orders_btn.clicked.connect(self._open_orders)
        header_layout.addWidget(self.orders_btn)

        self.logout_btn = QPushButton('Выйти')
        self.logout_btn.setStyleSheet(self._header_btn_style())
        self.logout_btn.clicked.connect(self._logout)
        header_layout.addWidget(self.logout_btn)

        main.addWidget(self.header)

        # Стек страниц
        self.stack = QStackedWidget()
        main.addWidget(self.stack)

        # Каталог
        self.catalog_view = CatalogView()
        self.catalog_view.product_selected.connect(self._open_product)
        self.stack.addWidget(self.catalog_view)

        # Заказы
        self.orders_view = OrdersView()
        self.orders_view.open_order.connect(self._open_order)
        self.orders_view.create_order.connect(self._create_order)
        self.orders_view.delete_order.connect(self._delete_order)
        self.stack.addWidget(self.orders_view)

    def _header_btn_style(self):
        return """
            QPushButton {
                background-color: transparent; color: white;
                padding: 6px 12px; border: 1px solid #4a6076;
                border-radius: 6px; font-size: 13px;
            }
            QPushButton:hover { background-color: #3a5169; }
        """

    def _refresh_header(self):
        user = current_user()
        if user:
            self.user_label.setText(user.full_name)
            self.orders_btn.setVisible(user.can_manage_orders)
        else:
            self.user_label.setText('Гость')
            self.orders_btn.setVisible(False)
        self.cart_btn.setText(f'🛒 Корзина ({len(self.cart)})')

    def _open_product(self, product_id):
        dialog = ProductView(product_id, self)
        dialog.add_to_cart.connect(self._add_to_cart)
        dialog.exec_()

    def _add_to_cart(self, stock_item_id, quantity, product_id):
        from models.product import get_product, get_sizes_for_product
        product = get_product(product_id)
        if not product:
            return
        size_value = ''
        for sid, sval, sqty in get_sizes_for_product(product_id):
            if sid == stock_item_id:
                size_value = sval
                break
        self.cart.append({
            'stock_item_id': stock_item_id,
            'quantity': quantity,
            'name': product.product_name,
            'manufacturer': product.manufacturer_name,
            'size': size_value,
            'price': product.final_price,
            'product_id': product_id,
        })
        self._refresh_header()

    def _open_cart(self):
        dialog = CartView(self)
        dialog.set_cart(self.cart)
        dialog.order_placed.connect(self._on_order_placed)
        dialog.exec_()

    def _on_order_placed(self):
        self.cart.clear()
        self._refresh_header()
        self.catalog_view.reload()

    def _open_orders(self):
        if not current_user() or not current_user().can_manage_orders:
            messages.show_warning(self, 'Доступ запрещён')
            return
        self.orders_view.reload()
        self.stack.setCurrentIndex(1)

    def _open_order(self, order_id):
        dialog = OrderEditView(order_id, self)
        dialog.changed = self.orders_view.reload
        dialog.exec_()

    def _create_order(self):
        from views.order_create_view import OrderCreateView
        if not current_user() or not current_user().can_manage_orders:
            messages.show_warning(self, 'Доступ запрещён')
            return
        dialog = OrderCreateView(self)
        dialog.order_created.connect(lambda _: self.orders_view.reload())
        dialog.exec_()

    def _delete_order(self, order_id):
        if not messages.ask_confirmation(self, f'Удалить заказ №{order_id}? Действие необратимо.'):
            return
        try:
            order_controller.remove_order(order_id)
        except Exception as e:
            messages.show_error(self, f'Ошибка удаления: {e}')
            return
        messages.show_info(self, 'Заказ удалён')
        self.orders_view.reload()

    def _logout(self):
        if not messages.ask_confirmation(self, 'Выйти из системы?'):
            return
        logout()
        self.cart.clear()
        self.close()