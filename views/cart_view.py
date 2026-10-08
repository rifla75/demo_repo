"""Корзина и оформление заказа."""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialogButtonBox, QHeaderView, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal

from controllers import order_controller
from controllers.auth_controller import current_user
from utils import messages


class CartView(QDialog):
    order_placed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Чудо Обувь — Корзина')
        self.resize(700, 480)
        self.cart = []
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        main = QVBoxLayout(self)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ['Товар', 'Размер', 'Кол-во', 'Цена', 'Сумма']
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main.addWidget(self.table)

        self.total_label = QLabel('Итого: 0.00 ₽')
        self.total_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #2c3e50;')
        self.total_label.setAlignment(Qt.AlignRight)
        main.addWidget(self.total_label)

        btns = QHBoxLayout()
        self.remove_btn = QPushButton('Удалить позицию')
        self.remove_btn.clicked.connect(self._remove_selected)
        btns.addWidget(self.remove_btn)
        btns.addStretch()

        self.checkout_btn = QPushButton('Оформить заказ')
        self.checkout_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white;
                          padding: 8px 20px; border-radius: 6px; }
            QPushButton:hover { background-color: #219150; }
        """)
        self.checkout_btn.clicked.connect(self._checkout)
        btns.addWidget(self.checkout_btn)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(self.reject)
        btns.addWidget(close_box)

        main.addLayout(btns)

    def set_cart(self, cart):
        self.cart = cart
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        total = 0
        for item in self.cart:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(
                f'{item["manufacturer"]} | {item["name"]}'))
            self.table.setItem(row, 1, QTableWidgetItem(str(item['size'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row, 3, QTableWidgetItem(f'{item["price"]:.2f}'))
            subtotal = item['quantity'] * item['price']
            self.table.setItem(row, 4, QTableWidgetItem(f'{subtotal:.2f}'))
            total += subtotal
        self.total_label.setText(f'Итого: {total:.2f} ₽')

    def _remove_selected(self):
        row = self.table.currentRow()
        if row < 0:
            messages.show_warning(self, 'Выберите позицию для удаления')
            return
        del self.cart[row]
        self._refresh()

    def _checkout(self):
        if not self.cart:
            messages.show_warning(self, 'Корзина пуста')
            return
        user = current_user()
        if not user:
            messages.show_error(self, 'Требуется авторизация')
            return

        items = [{'stock_item_id': it['stock_item_id'], 'quantity': it['quantity']}
                 for it in self.cart]
        try:
            order_id = order_controller.place_order(user.user_id, items)
        except Exception as e:
            messages.show_error(self, f'Не удалось оформить заказ:\n{e}')
            return

        messages.show_info(self, f'Заказ №{order_id} успешно оформлен!')
        self.cart.clear()
        self._refresh()
        self.order_placed.emit()
        self.accept()