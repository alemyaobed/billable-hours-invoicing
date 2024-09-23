"""
Test suite for the utility functions in the invoices app.
"""
from django.test import TestCase
from invoices.utils import convert_decimal_to_string
from decimal import Decimal


class ConvertDecimalToStringTest(TestCase):
    """
    Test suite for the convert_decimal_to_string utility function.
    """

    def test_convert_decimal_in_dict(self):
        """
        Test conversion of Decimal objects inside a dictionary.
        Ensures that Decimal values are converted to strings and
        rounded to 2 decimal places.
        """
        data = {
            "price": Decimal("100.5034343"),
            "weight": Decimal("200.7"),
            "height": Decimal("300.125456"),
            "length": Decimal("400.999"),
            "width": Decimal("2.5123"),
            "amount": Decimal("2.500"),
            "details": {
                "cost": Decimal("200.75")
            }
        }
        result = convert_decimal_to_string(data)
        self.assertEqual(result, {
            "price": "100.50",
            "weight": "200.70",
            "height": "300.13",
            "length": "401.00",
            "width": "2.51",
            "amount": "2.50",
            "details": {
                "cost": "200.75"
            }
        })

    def test_convert_no_decimal(self):
        """
        Test a dictionary with no Decimal objects.
        Ensures that the original dictionary remains unchanged.
        """
        data = {
            "name": "John Doe",
            "age": 30,
            "height": 179.6,
            "is_active": True
        }
        result = convert_decimal_to_string(data)
        self.assertEqual(
            result,
            {
                "name": "John Doe",
                "age": 30,
                "height": 179.6,
                "is_active": True
            }
        )
