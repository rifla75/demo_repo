"""Окно ручного создания заказа (Менеджер/Администратор)."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialogButtonBox, QLineEdit, QWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

from models.user import list_all as list_all_users
from models.product import search_products, get_sizes_for_product
from controllers import order_controller
from utils import messages


class OrderCreateView(QDialog):
    """Диалог ручного создания заказа."""

    order_created = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Чудо Обувь — Новый заказ')
        self.resize(900, 620)
        self.items = []
        self._build_ui()
        self._load_clients()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # --- Шапка: клиент + дата ---
        top = QHBoxLayout()
        top.addWidget(QLabel('Клиент:'))
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(250)
        top.addWidget(self.client_combo)

        top.addWidget(QLabel('Дата заказа:'))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        top.addWidget(self.date_edit)

        top.addStretch()
        main.addLayout(top)

        # --- Блок добавления позиции ---
        add_box = QHBoxLayout()

        add_box.addWidget(QLabel('Поиск:'))
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText('Введите название товара...')
        self.product_input.textChanged.connect(self._on_product_search)
        add_box.addWidget(self.product_input, 2)

        add_box.addWidget(QLabel('Товар:'))
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(250)
        self.product_combo.currentIndexChanged.connect(self._on_product_selected)
        add_box.addWidget(self.product_combo, 2)

        main.addLayout(add_box)

        # --- Размер, количество, цена, кнопка добавления ---
        add_box2 = QHBoxLayout()
        add_box2.addWidget(QLabel('Размер:'))
        self.size_combo = QComboBox()
        add_box2.addWidget(self.size_combo)

        add_box2.addWidget(QLabel('Кол-во:'))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(999)
        add_box2.addWidget(self.qty_spin)

        add_box2.addWidget(QLabel('Цена:'))
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0)
        self.price_spin.setMaximum(999999)
        self.price_spin.setDecimals(2)
        add_box2.addWidget(self.price_spin)

        add_box2.addStretch()

        self.add_btn = QPushButton('Добавить позицию')
        self.add_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white;
                          padding: 6px 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.add_btn.clicked.connect(self._on_add_item)
        add_box2.addWidget(self.add_btn)

        main.addLayout(add_box2)

        # --- Таблица позиций ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ['Товар', 'Производитель', 'Размер', 'Кол-во', 'Цена', 'Сумма']
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main.addWidget(self.table)

        # --- Итог ---
        self.total_label = QLabel('Итого: 0.00 ₽')
        self.total_label.setStyleSheet(
            'font-size: 16px; font-weight: bold; color: #2c3e50;'
        )
        self.total_label.setAlignment(Qt.AlignRight)
        main.addWidget(self.total_label)

        # --- Кнопки ---
        btns = QHBoxLayout()
        self.remove_btn = QPushButton('Удалить позицию')
        self.remove_btn.clicked.connect(self._on_remove_item)
        btns.addWidget(self.remove_btn)
        btns.addStretch()

        save_btn = QPushButton('Создать заказ')
        save_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white;
                          padding: 8px 20px; border-radius: 6px; }
            QPushButton:hover { background-color: #219150; }
        """)
        save_btn.clicked.connect(self._on_save)
        btns.addWidget(save_btn)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(self.reject)
        btns.addWidget(close_box)

        main.addLayout(btns)

    def _load_clients(self):
        self.client_combo.clear()
        self.client_combo.addItem('— выберите клиента —', None)
        try:
            for user in list_all_users():
                self.client_combo.addItem(
                    f'{user.full_name} ({user.login})', user.user_id
                )
        except Exception as e:
            messages.show_error(self, f'Не удалось загрузить клиентов:\n{e}')

    def _on_product_search(self, text):
        self.product_combo.clear()
        self.size_combo.clear()
        if not text or len(text.strip()) < 2:
            return
        try:
            results = search_products(text.strip())
        except Exception:
            return
        for pid, name, manufacturer, price in results:
            self.product_combo.addItem(
                f'{manufacturer} | {name} — {price:.2f} ₽',
                (pid, float(price))
            )

    def _on_product_selected(self, index):
        self.size_combo.clear()
        data = self.product_combo.currentData()
        if not data:
            return
        product_id, price = data
        self.price_spin.setValue(price)
        try:
            sizes = get_sizes_for_product(product_id)
        except Exception:
            return
        for stock_id, size_value, qty in sizes:
            if qty > 0:
                self.size_combo.addItem(
                    f'{size_value} ({qty} шт.)', (stock_id, qty)
                )

    def _on_add_item(self):
        product_data = self.product_combo.currentData()
        size_data = self.size_combo.currentData()

        if not product_data:
            messages.show_warning(self, 'Выберите товар')
            return
        if not size_data:
            messages.show_warning(
                self, 'Выберите размер (или товар отсутствует на складе)'
            )
            return

        product_id, _ = product_data
        stock_id, max_qty = size_data
        qty = self.qty_spin.value()
        price = self.price_spin.value()

        if qty <= 0 or qty > max_qty:
            messages.show_error(self, f'Количество должно быть от 1 до {max_qty}')
            return
        if price <= 0:
            messages.show_error(self, 'Цена должна быть больше нуля')
            return

        for item in self.items:
            if item['stock_item_id'] == stock_id:
                new_qty = item['quantity'] + qty
                if new_qty > max_qty:
                    messages.show_error(
                        self,
                        f'Суммарное количество превышает остаток ({max_qty} шт.)'
                    )
                    return
                item['quantity'] = new_qty
                self._refresh_table()
                return

        text = self.product_combo.currentText()
        parts = text.split('|')
        manufacturer = parts[0].strip() if len(parts) > 1 else ''
        name_part = parts[1].split('—')[0].strip() if len(parts) > 1 else text

        size_text = self.size_combo.currentText().split('(')[0].strip()

        self.items.append({
            'stock_item_id': stock_id,
            'quantity': qty,
            'price': price,
            'name': name_part,
            'manufacturer': manufacturer,
            'size': size_text,
        })
        self._refresh_table()

    def _on_remove_item(self):
        row = self.table.currentRow()
        if row < 0:
            messages.show_warning(self, 'Выберите позицию для удаления')
            return
        del self.items[row]
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        total = 0.0
        for item in self.items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row, 1, QTableWidgetItem(item['manufacturer']))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['size'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row, 4, QTableWidgetItem(f'{item["price"]:.2f}'))
            subtotal = item['quantity'] * item['price']
            self.table.setItem(row, 5, QTableWidgetItem(f'{subtotal:.2f}'))
            total += subtotal
        self.total_label.setText(f'Итого: {total:.2f} ₽')

    def _on_save(self):
        client_id = self.client_combo.currentData()
        if not client_id:
            messages.show_warning(self, 'Выберите клиента')
            return
        if not self.items:
            messages.show_warning(self, 'Добавьте хотя бы одну позицию')
            return

        order_date = self.date_edit.date().toString('yyyy-MM-dd')
        items_payload = [
            {
                'stock_item_id': it['stock_item_id'],
                'quantity': it['quantity'],
                'price': it['price'],
            }
            for it in self.items
        ]

        try:
            order_id = order_controller.place_manual_order(
                client_id, order_date, items_payload
            )
        except Exception as e:
            messages.show_error(self, f'Не удалось создать заказ:\n{e}')
            return

        messages.show_info(self, f'Заказ №{order_id} успешно создан!')
        self.order_created.emit(order_id)
        self.accept()