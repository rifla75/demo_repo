"""Список заказов (Менеджер/Администратор)."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLabel)
from PyQt5.QtCore import Qt, pyqtSignal

from controllers import order_controller
from utils import messages


class OrdersView(QWidget):
    open_order = pyqtSignal(int)
    create_order = pyqtSignal()
    delete_order = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel('Список заказов')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50;')
        header.addWidget(title)
        header.addStretch()

        self.add_btn = QPushButton('+ Новый заказ')
        self.add_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white;
                          padding: 6px 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.add_btn.clicked.connect(self.create_order.emit)
        header.addWidget(self.add_btn)

        self.refresh_btn = QPushButton('Обновить')
        self.refresh_btn.clicked.connect(self.reload)
        header.addWidget(self.refresh_btn)

        main.addLayout(header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['№', 'Дата', 'ФИО клиента', 'Действия'])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        main.addWidget(self.table)

    def reload(self):
        self.table.setRowCount(0)
        try:
            orders = order_controller.get_all_orders()
        except Exception as e:
            messages.show_error(self, f'Ошибка загрузки заказов:\n{e}')
            return
        for order in orders:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(order.order_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(order.order_date)))
            self.table.setItem(row, 2, QTableWidgetItem(order.fio))

            open_btn = QPushButton('Открыть')
            open_btn.clicked.connect(
                lambda _, oid=order.order_id: self.open_order.emit(oid))

            del_btn = QPushButton('Удалить')
            del_btn.setStyleSheet('background-color: #e74c3c; color: white;')
            del_btn.clicked.connect(
                lambda _, oid=order.order_id: self.delete_order.emit(oid))

            wrapper = QWidget()
            wl = QHBoxLayout(wrapper)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.addWidget(open_btn)
            wl.addWidget(del_btn)
            self.table.setCellWidget(row, 3, wrapper)

    def _on_double_click(self, row, col):
        item = self.table.item(row, 0)
        if item:
            self.open_order.emit(int(item.text()))