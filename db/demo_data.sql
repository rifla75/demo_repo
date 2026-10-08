-- Демо-данные для «Чудо Обувь»

-- 1. Категории и производители (на случай, если seed.sql не применён)
INSERT INTO categories (category_name) VALUES
    ('Детская обувь'), ('Женская обувь'), ('Мужская обувь')
ON CONFLICT DO NOTHING;

INSERT INTO manufacturers (manufacturer_name) VALUES
    ('Малыш-Спорт'), ('Топ-Топ'), ('Барбари'), ('Стиль и комфорт')
ON CONFLICT DO NOTHING;

-- 2. Пользователи (3 роли)
INSERT INTO users (last_name, first_name, middle_name, login, role_id)
VALUES 
    ('Иванов', 'Иван', 'Иванович', 'isivanov',
        (SELECT role_id FROM roles WHERE role_name = 'Администратор')),
    ('Петров', 'Павел', 'Петрович', 'papetrov',
        (SELECT role_id FROM roles WHERE role_name = 'Менеджер')),
    ('Сидорова', 'Анна', 'Сергеевна', 'asidorova',
        (SELECT role_id FROM roles WHERE role_name = 'Авторизованный пользователь'))
ON CONFLICT (login) DO NOTHING;

-- 3. Размеры
INSERT INTO sizes (size_value) VALUES
    ('35'), ('36'), ('37'), ('38'), ('39'), ('40'),
    ('41'), ('42'), ('43'), ('44'), ('45')
ON CONFLICT (size_value) DO NOTHING;

-- 4. Товары
INSERT INTO products (category_id, manufacturer_id, subcategory, product_name,
                      image_path, description, composition, price)
VALUES
    ((SELECT category_id FROM categories WHERE category_name = 'Женская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Стиль и комфорт'),
     'Туфли', 'Туфли женские классические',
     'IMG_01.png', 'Элегантные туфли на каблуке для повседневной носки.',
     'Натуральная кожа', 4500.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Женская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Барбари'),
     'Кроссовки', 'Кроссовки женские спортивные',
     'IMG_02.png', 'Удобные кроссовки для бега и прогулок.',
     'Текстиль, резина', 3200.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Мужская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Стиль и комфорт'),
     'Ботинки', 'Ботинки мужские кожаные',
     'IMG_03.png', 'Прочные ботинки для осенне-зимнего сезона.',
     'Натуральная кожа', 6800.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Мужская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Топ-Топ'),
     'Кроссовки', 'Кроссовки мужские',
     'IMG_04.png', 'Лёгкие кроссовки для активного отдыха.',
     'Текстиль', 2900.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Детская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Малыш-Спорт'),
     'Кроссовки', 'Кроссовки детские',
     'IMG_05.png', 'Яркие кроссовки для детей.',
     'Текстиль', 1800.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Детская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Барбари'),
     'Сандалии', 'Сандалии детские',
     'IMG_06.png', 'Лёгкие сандалии для лета.',
     'Кожа, текстиль', 1500.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Женская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Барбари'),
     'Сапоги', 'Сапоги женские зимние',
     'IMG_07.png', 'Тёплые сапоги для суровой зимы.',
     'Натуральная кожа, мех', 8500.00),

    ((SELECT category_id FROM categories WHERE category_name = 'Мужская обувь'),
     (SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name = 'Стиль и комфорт'),
     'Туфли', 'Туфли мужские классические',
     'IMG_08.png', 'Строгие туфли для деловых встреч.',
     'Натуральная кожа', 5500.00)
ON CONFLICT (product_name, manufacturer_id) DO NOTHING;

-- 5. Склад: размеры 37-42, по 10 шт.
INSERT INTO stock_items (product_id, size_id, quantity_available)
SELECT p.product_id, s.size_id, 10
FROM products p CROSS JOIN sizes s
WHERE s.size_value IN ('37', '38', '39', '40', '41', '42')
ON CONFLICT (product_id, size_id) DO NOTHING;

-- 6. Товар с малым остатком (для подсветки ≤ 3)
UPDATE stock_items
SET quantity_available = 2
WHERE product_id = (
    SELECT product_id FROM products 
    WHERE product_name = 'Кроссовки женские спортивные'
)
AND size_id = (SELECT size_id FROM sizes WHERE size_value = '37');