-- Демо-данные
INSERT INTO categories (category_name) VALUES
    ('Детская обувь'),
    ('Женская обувь'),
    ('Мужская обувь')
ON CONFLICT DO NOTHING;

INSERT INTO manufacturers (manufacturer_name) VALUES
    ('Малыш-Спорт'),
    ('Топ-Топ'),
    ('Барбари'),
    ('Стиль и комфорт')
ON CONFLICT DO NOTHING;
