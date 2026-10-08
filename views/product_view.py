"""Форма просмотра товара."""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QComboBox, QFrame,
                             QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from controllers import catalog_controller
from utils import messages
import os

RES_IMG_DIR = 'resources/images'


class ProductView(QDialog):
    add_to_cart = pyqtSignal(int, int, int)

    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.product = None
        self.sizes = []
        self.setWindowTitle('Чудо Обувь — Просмотр товара')
        self.resize(700, 560)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        main = QVBoxLayout(self)

        top = QHBoxLayout()

        self.img_label = QLabel()
        self.img_label.setFixedSize(220, 180)
        self.img_label.setStyleSheet('background: #fafafa; border-radius: 8px;')
        self.img_label.setAlignment(Qt.AlignCenter)
        top.addWidget(self.img_label)

        info = QFormLayout()
        self.title_label = QLabel()
        self.title_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50;')
        info.addRow(self.title_label)
        self.category_label = QLabel()
        info.addRow('Категория:', self.category_label)
        self.manufacturer_label = QLabel()
        info.addRow('Производство:', self.manufacturer_label)
        self.price_label = QLabel()
        self.price_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #27ae60;')
        info.addRow('Цена со скидкой:', self.price_label)
        self.composition_label = QLabel()
        self.composition_label.setWordWrap(True)
        info.addRow('Состав:', self.composition_label)
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        info.addRow('Описание:', self.description_label)

        top.addLayout(info, 1)
        main.addLayout(top)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet('color: #ddd;')
        main.addWidget(line)

        form = QHBoxLayout()
        form.addWidget(QLabel('Размер:'))
        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self._on_size_changed)
        form.addWidget(self.size_combo)

        form.addWidget(QLabel('Количество:'))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(1)
        form.addWidget(self.qty_spin)

        self.available_label = QLabel('')
        self.available_label.setStyleSheet('color: #666;')
        form.addWidget(self.available_label)

        form.addStretch()
        self.add_btn = QPushButton('Добавить в корзину')
        self.add_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white;
                          padding: 8px 20px; border-radius: 6px; }
            QPushButton:hover { background-color: #219150; }
        """)
        self.add_btn.clicked.connect(self._on_add)
        form.addWidget(self.add_btn)
        main.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        main.addWidget(buttons)

    def _load_data(self):
        product, sizes = catalog_controller.get_product_details(self.product_id)
        if not product:
            messages.show_error(self, 'Товар не найден')
            self.reject()
            return
        self.product = product
        self.sizes = sizes

        img_path = None
        if product.image_path:
            candidate = os.path.join(RES_IMG_DIR, product.image_path)
            if os.path.exists(candidate):
                img_path = candidate
        if not img_path:
            candidate = os.path.join(RES_IMG_DIR, 'picture.png')
            if os.path.exists(candidate):
                img_path = candidate
        if img_path:
            pix = QPixmap(img_path)
            if not pix.isNull():
                self.img_label.setPixmap(pix.scaled(220, 180, Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation))

        self.title_label.setText(f'{product.manufacturer_name} | {product.product_name}')
        self.category_label.setText(product.category_name)
        self.manufacturer_label.setText(product.manufacturer_name)

        price_text = f'{product.final_price:.2f} ₽'
        if product.discount_percent:
            price_text += f'  (скидка {product.discount_percent}%, было {product.base_price:.2f} ₽)'
        self.price_label.setText(price_text)

        self.composition_label.setText(product.composition)
        self.description_label.setText(product.description)

        self.size_combo.clear()
        for stock_id, size_value, qty in sizes:
            self.size_combo.addItem(f'{size_value} ({qty} шт.)', (stock_id, qty))
        self._on_size_changed()

    def _on_size_changed(self):
        data = self.size_combo.currentData()
        if data:
            stock_id, qty = data
            self.qty_spin.setMaximum(max(1, qty))
            self.qty_spin.setValue(1)
            self.available_label.setText(f'Доступно: {qty} шт.')

    def _on_add(self):
        data = self.size_combo.currentData()
        if not data:
            messages.show_warning(self, 'Выберите размер')
            return
        stock_id, qty = data
        if qty <= 0:
            messages.show_warning(self, 'Товар отсутствует на складе')
            return
        count = self.qty_spin.value()
        if count <= 0 or count > qty:
            messages.show_error(self, f'Количество должно быть от 1 до {qty}')
            return
        self.add_to_cart.emit(stock_id, count, self.product_id)
        messages.show_info(self, 'Товар добавлен в корзину')