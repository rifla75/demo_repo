"""Тесты для controllers/discount.py (с моками БД)."""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers import discount


class TestPreviousMonthRange(unittest.TestCase):

    @patch('controllers.discount.datetime')
    def test_range(self, mock_dt):
        mock_dt.now.return_value.date.return_value = date(2026, 10, 8)
        start, end = discount.get_previous_month_range()
        self.assertEqual(start, date(2026, 9, 1))
        self.assertEqual(end, date(2026, 10, 1))

    @patch('controllers.discount.datetime')
    def test_range_january(self, mock_dt):
        mock_dt.now.return_value.date.return_value = date(2026, 1, 15)
        start, end = discount.get_previous_month_range()
        self.assertEqual(start, date(2025, 12, 1))
        self.assertEqual(end, date(2026, 1, 1))


class TestCalculateFinalPrice(unittest.TestCase):

    @patch('controllers.discount.has_orders_last_month', return_value=True)
    def test_no_discount_when_orders_exist(self, mock_has):
        final, pct = discount.calculate_final_price(1, 1000.0)
        self.assertEqual(final, 1000.0)
        self.assertEqual(pct, 0)

    @patch('controllers.discount.has_orders_last_month', return_value=False)
    def test_discount_25_percent(self, mock_has):
        final, pct = discount.calculate_final_price(1, 1000.0)
        self.assertEqual(final, 750.0)
        self.assertEqual(pct, 25)

    @patch('controllers.discount.has_orders_last_month', return_value=False)
    def test_discount_rounding(self, mock_has):
        final, pct = discount.calculate_final_price(1, 999.99)
        self.assertEqual(final, 749.99)
        self.assertEqual(pct, 25)

    @patch('controllers.discount.has_orders_last_month', return_value=False)
    def test_discount_zero_price(self, mock_has):
        final, pct = discount.calculate_final_price(1, 0)
        self.assertEqual(final, 0)
        self.assertEqual(pct, 25)


if __name__ == '__main__':
    unittest.main()