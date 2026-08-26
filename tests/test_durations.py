import unittest

from throughputkit.durations import format_duration, parse_duration


class ParseDurationTests(unittest.TestCase):
    def test_bare_number_is_seconds(self):
        self.assertEqual(parse_duration("90"), 90.0)
        self.assertEqual(parse_duration("0"), 0.0)

    def test_single_unit(self):
        self.assertEqual(parse_duration("2h"), 7200.0)
        self.assertEqual(parse_duration("500ms"), 0.5)

    def test_compound(self):
        self.assertEqual(parse_duration("1m30s"), 90.0)
        self.assertEqual(parse_duration("1d 2h 3m"), 93_780.0)

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(parse_duration("  2h  "), 7200.0)

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            parse_duration("")
        with self.assertRaises(ValueError):
            parse_duration("   ")

    def test_rejects_leftover_characters(self):
        with self.assertRaises(ValueError):
            parse_duration("1x")

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_duration("abc")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            parse_duration("-5")

    def test_rejects_non_finite(self):
        # float() accepts "inf"/"nan" strings; those aren't valid durations.
        with self.assertRaises(ValueError):
            parse_duration("inf")
        with self.assertRaises(ValueError):
            parse_duration("nan")

    def test_rejects_overflow(self):
        # A token sum that overflows past float's range should raise
        # ValueError, not silently return inf.
        with self.assertRaises(ValueError):
            parse_duration("1" + "0" * 400 + "d")


class FormatDurationTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_duration(0), "0s")

    def test_sub_second(self):
        self.assertEqual(format_duration(0.25), "250ms")

    def test_whole_units(self):
        self.assertEqual(format_duration(60), "1m")
        self.assertEqual(format_duration(86400), "1d")

    def test_compound(self):
        self.assertEqual(format_duration(3725), "1h 2m 5s")

    def test_fractional_remainder(self):
        self.assertEqual(format_duration(90.5), "1m 30.50s")

    def test_sub_minute_fractional(self):
        self.assertEqual(format_duration(59.99), "59.99s")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            format_duration(-1)


if __name__ == "__main__":
    unittest.main()
