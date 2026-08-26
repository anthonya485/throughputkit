import unittest

from throughputkit.sizes import format_bytes, parse_bytes


class ParseBytesTests(unittest.TestCase):
    def test_bare_number(self):
        self.assertEqual(parse_bytes("512"), 512)
        self.assertEqual(parse_bytes("0"), 0)

    def test_decimal_units(self):
        self.assertEqual(parse_bytes("1.5MB"), 1_500_000)
        self.assertEqual(parse_bytes("2KB"), 2000)

    def test_binary_units(self):
        self.assertEqual(parse_bytes("2GiB"), 2 * 1024**3)
        self.assertEqual(parse_bytes("900K"), 921_600)

    def test_case_insensitive(self):
        self.assertEqual(parse_bytes("1kb"), 1000)
        self.assertEqual(parse_bytes("1Gib"), 1024**3)

    def test_whitespace_tolerant(self):
        self.assertEqual(parse_bytes(" 5 KB "), 5000)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_bytes("abc")

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            parse_bytes("")

    def test_rejects_unknown_unit(self):
        with self.assertRaises(ValueError):
            parse_bytes("5XB")

    def test_rejects_malformed_number(self):
        with self.assertRaises(ValueError):
            parse_bytes("5.5.5MB")

    def test_rejects_negative(self):
        # The regex has no sign handling, so a leading "-" fails to match
        # rather than silently producing a negative byte count.
        with self.assertRaises(ValueError):
            parse_bytes("-5MB")

    def test_rejects_overflow(self):
        # A finite input number can still overflow past float's range once
        # multiplied by a PB-scale multiplier; that should raise ValueError
        # rather than the OverflowError int() would otherwise produce.
        with self.assertRaises(ValueError):
            parse_bytes("1" + "0" * 300 + "PB")


class FormatBytesTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_bytes(0), "0 B")

    def test_binary_default(self):
        self.assertEqual(format_bytes(1536), "1.5 KiB")

    def test_decimal(self):
        self.assertEqual(format_bytes(1536, binary=False), "1.5 KB")

    def test_precision(self):
        self.assertEqual(format_bytes(1600, binary=False, precision=0), "2 KB")

    def test_caps_at_largest_unit(self):
        # A value beyond the PiB range should stay expressed in PiB rather
        # than raising or inventing a bigger unit.
        self.assertEqual(format_bytes(1024**6), "1024.0 PiB")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            format_bytes(-1)


if __name__ == "__main__":
    unittest.main()
