"""Логика каталога."""
from models.product import list_products, get_product, get_sizes_for_product, list_categories


def get_catalog(category_id=None, search='', sort=''):
    return list_products(category_id=category_id, search=search, sort=sort)


def get_product_details(product_id):
    product = get_product(product_id)
    if not product:
        return None, []
    sizes = get_sizes_for_product(product_id)
    return product, sizes


def get_all_categories():
    return list_categories()
