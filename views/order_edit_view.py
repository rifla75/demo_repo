"""Просмотр/редактирование заказа."""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QDateEdit, QDialogButtonBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate

from controllers import order_controller
from controllers.auth_controller import current_user
from utils import messages


class OrderEditView(QDialog):
    changed = None

    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.order = None
        self.is_admin = bool(current_user() and current_user().is_admin)
        self.setWindowTitle(f'Чудо Обувь — Заказ №{order_id}')
        self.resize(750, 520)
        self._build_ui()
        self._load()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # Шапка
        top = QHBoxLayout()
        top.addWidget(QLabel('Дата заказа:'))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(self.is_admin)
        top.addWidget(self.date_edit)
        top.addWidget(QLabel('Клиент:'))
        self.client_label = QLabel('')
        self.client_label.setStyleSheet('font-weight: bold;')
        top.addWidget(self.client_label)
        top.addStretch()
        main.addLayout(top)

        # Таблица позиций
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ['Товар', 'Произв.', 'Размер', 'Кол-во', 'Цена', 'Сумма']
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main.addWidget(self.table)

        # Итог
        self.total_label = QLabel('')
        self.total_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.total_label.setAlignment(Qt.AlignRight)
        main.addWidget(self.total_label)

        # Кнопки
        btns = QHBoxLayout()
        if self.is_admin:
            self.del_item_btn = QPushButton('Удалить позицию')
            self.del_item_btn.clicked.connect(self._remove_item)
            btns.addWidget(self.del_item_btn)
        btns.addStretch()

        if self.is_admin:
            save_btn = QPushButton('Сохранить изменения')
            save_btn.setStyleSheet("""
                QPushButton { background-color: #27ae60; color: white;
                              padding: 8px 20px; border-radius: 6px; }
            """)
            save_btn.clicked.connect(self._save)
            btns.addWidget(save_btn)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(self.reject)
        btns.addWidget(close_box)
        main.addLayout(btns)

        self.removed_items = []

    def _load(self):
        order = order_controller.get_order_details(self.order_id)
        if not order:
            messages.show_error(self, 'Заказ не найден')
            self.reject()
            return
        self.order = order
        self.client_label.setText(order.fio)
        self.date_edit.setDate(QDate.fromString(str(order.order_date), 'yyyy-MM-dd'))
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        total = 0
        for it in self.order.items:
            item_id, qty, price, pname, mname, size = it
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(pname))
            self.table.setItem(row, 1, QTableWidgetItem(mname))
            self.table.setItem(row, 2, QTableWidgetItem(str(size)))
            self.table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.table.setItem(row, 4, QTableWidgetItem(f'{float(price):.2f}'))
            self.table.setItem(row, 5, QTableWidgetItem(f'{qty * float(price):.2f}'))
            total += qty * float(price)
        self.total_label.setText(f'Итого: {total:.2f} ₽')

    def _remove_item(self):
        row = self.table.currentRow()
        if row < 0:
            messages.show_warning(self, 'Выберите позицию')
            return
        if not messages.ask_confirmation(self, 'Удалить выбранную позицию из заказа?'):
            return
        item_id = self.order.items[row][0]
        self.removed_items.append(item_id)
        self.order.items = [it for it in self.order.items if it[0] != item_id]
        self._refresh_table()

    def _save(self):
        new_date = self.date_edit.date().toString('yyyy-MM-dd')
        try:
            order_controller.edit_order(self.order_id, new_date, self.removed_items)
        except Exception as e:
            messages.show_error(self, f'Ошибка сохранения: {e}')
            return
        messages.show_info(self, 'Изменения сохранены')
        if self.changed:
            self.changed()
        self.accept()