"""Тесты для utils/validators.py."""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import is_positive_int, validate_quantity


class TestIsPositiveInt(unittest.TestCase):

    def test_positive(self):
        self.assertTrue(is_positive_int('5'))
        self.assertTrue(is_positive_int(10))
        self.assertTrue(is_positive_int('1'))

    def test_zero(self):
        self.assertFalse(is_positive_int('0'))
        self.assertFalse(is_positive_int(0))

    def test_negative(self):
        self.assertFalse(is_positive_int('-3'))
        self.assertFalse(is_positive_int(-1))

    def test_not_a_number(self):
        self.assertFalse(is_positive_int('abc'))
        self.assertFalse(is_positive_int(''))
        self.assertFalse(is_positive_int(None))

    def test_float_string(self):
        self.assertFalse(is_positive_int('3.5'))


class TestValidateQuantity(unittest.TestCase):

    def test_valid(self):
        ok, msg = validate_quantity('5', 10)
        self.assertTrue(ok)
        self.assertEqual(msg, '')

    def test_empty(self):
        ok, msg = validate_quantity('', 10)
        self.assertFalse(ok)
        self.assertIn('Введите', msg)

    def test_not_int(self):
        ok, msg = validate_quantity('abc', 10)
        self.assertFalse(ok)
        self.assertIn('целым', msg)

    def test_zero(self):
        ok, msg = validate_quantity('0', 10)
        self.assertFalse(ok)
        self.assertIn('положительным', msg)

    def test_negative(self):
        ok, msg = validate_quantity('-2', 10)
        self.assertFalse(ok)

    def test_exceeds_max(self):
        ok, msg = validate_quantity('15', 10)
        self.assertFalse(ok)
        self.assertIn('10', msg)

    def test_exactly_max(self):
        ok, msg = validate_quantity('10', 10)
        self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()