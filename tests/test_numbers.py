import unittest

from throughputkit._numbers import parse_localized_number


class ParseLocalizedNumberTests(unittest.TestCase):
    def test_plain_integer(self):
        self.assertEqual(parse_localized_number("1234"), 1234.0)

    def test_single_dot_is_decimal(self):
        self.assertEqual(parse_localized_number("1.5"), 1.5)

    def test_single_comma_is_decimal(self):
        self.assertEqual(parse_localized_number("1,5"), 1.5)

    def test_repeated_comma_is_grouping(self):
        self.assertEqual(parse_localized_number("1,234,567"), 1234567.0)

    def test_repeated_dot_is_grouping(self):
        self.assertEqual(parse_localized_number("1.234.567"), 1234567.0)

    def test_dot_grouping_comma_decimal(self):
        self.assertEqual(parse_localized_number("1.234.567,89"), 1234567.89)

    def test_comma_grouping_dot_decimal(self):
        self.assertEqual(parse_localized_number("1,234,567.89"), 1234567.89)

    def test_rejects_short_leading_group(self):
        with self.assertRaises(ValueError):
            parse_localized_number("1234,567,890")

    def test_rejects_short_trailing_group(self):
        with self.assertRaises(ValueError):
            parse_localized_number("1,23,456")

    def test_rejects_non_numeric_group(self):
        with self.assertRaises(ValueError):
            parse_localized_number("1,2a4,567")


if __name__ == "__main__":
    unittest.main()
