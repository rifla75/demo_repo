"""Каталог товаров."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QComboBox, QScrollArea, QFrame, QLabel,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from controllers import catalog_controller

import os


RES_IMG_DIR = 'resources/images'


class ProductCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, product):
        super().__init__()
        self.product = product
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        if product.is_low_stock:
            self.setStyleSheet("""
                ProductCard {
                    background-color: #ffe0e0;
                    border: 1px solid #e0b0b0;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                ProductCard {
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 8px;
                }
                ProductCard:hover {
                    border: 1px solid #3498db;
                }
            """)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Изображение
        img_label = QLabel()
        img_label.setFixedSize(140, 110)
        img_label.setStyleSheet('background: #fafafa; border-radius: 6px;')
        img_label.setAlignment(Qt.AlignCenter)

        img_path = None
        if self.product.image_path:
            candidate = os.path.join(RES_IMG_DIR, self.product.image_path)
            if os.path.exists(candidate):
                img_path = candidate
        if not img_path:
            candidate = os.path.join(RES_IMG_DIR, 'picture.png')
            if os.path.exists(candidate):
                img_path = candidate

        if img_path:
            pix = QPixmap(img_path)
            if not pix.isNull():
                img_label.setPixmap(pix.scaled(140, 110, Qt.KeepAspectRatio,
                                                Qt.SmoothTransformation))
        layout.addWidget(img_label)

        # Информация
        info = QVBoxLayout()

        title_row = QHBoxLayout()
        title = QLabel(f'{self.product.manufacturer_name} | {self.product.product_name}')
        title.setStyleSheet('font-size: 15px; font-weight: bold; color: #2c3e50;')
        title_row.addWidget(title)
        title_row.addStretch()

        price_text = f'{self.product.final_price:.2f} ₽'
        if self.product.discount_percent:
            price_text += f'  (скидка {self.product.discount_percent}%)'
        price = QLabel(price_text)
        price.setStyleSheet('font-size: 15px; font-weight: bold; color: #27ae60;')
        title_row.addWidget(price)
        info.addLayout(title_row)

        cat = QLabel(f'Категория: {self.product.category_name}')
        cat.setStyleSheet('color: #555;')
        info.addWidget(cat)

        qty = QLabel(f'Количество: {self.product.availability} ({self.product.total_quantity})')
        qty.setStyleSheet('color: #555;')
        info.addWidget(qty)

        comp = QLabel(f'Состав: {self.product.composition}')
        comp.setWordWrap(True)
        comp.setStyleSheet('color: #777; font-size: 12px;')
        info.addWidget(comp)

        layout.addLayout(info, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(140)

    def mousePressEvent(self, event):
        self.clicked.emit(self.product.product_id)


class CatalogView(QWidget):
    product_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.reload()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)

        # Фильтры
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍 Поиск по названию и описанию')
        self.search_input.textChanged.connect(self._on_filter_changed)
        filters.addWidget(self.search_input, 2)

        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self._on_filter_changed)
        filters.addWidget(self.category_combo, 1)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem('Без сортировки', '')
        self.sort_combo.addItem('Цена ↑', 'price_asc')
        self.sort_combo.addItem('Цена ↓', 'price_desc')
        self.sort_combo.currentIndexChanged.connect(self._on_filter_changed)
        filters.addWidget(self.sort_combo, 1)

        main.addLayout(filters)

        # Список товаров
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet('QScrollArea { border: none; }')

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.list_widget)
        main.addWidget(self.scroll)

    def _load_categories(self):
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem('Все категории', None)
        for cat_id, cat_name in catalog_controller.get_all_categories():
            self.category_combo.addItem(cat_name, cat_id)
        self.category_combo.blockSignals(False)

    def _on_filter_changed(self):
        self.reload()

    def reload(self):
        # Очистка
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Загрузка категорий при первом вызове
        if self.category_combo.count() == 0:
            self._load_categories()

        # Параметры
        category_id = self.category_combo.currentData()
        search = self.search_input.text()
        sort = self.sort_combo.currentData()

        # Получение товаров
        try:
            products = catalog_controller.get_catalog(
                category_id=category_id, search=search, sort=sort
            )
        except Exception as e:
            err = QLabel(f'Ошибка загрузки каталога: {e}')
            err.setAlignment(Qt.AlignCenter)
            err.setStyleSheet('color: #c0392b; font-size: 14px; padding: 40px;')
            self.list_layout.addWidget(err)
            return

        if not products:
            empty = QLabel('Товары не найдены')
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet('color: #888; font-size: 16px; padding: 40px;')
            self.list_layout.addWidget(empty)
            return

        for product in products:
            card = ProductCard(product)
            card.clicked.connect(self.product_selected.emit)
            self.list_layout.addWidget(card)