import unittest
from pysvglabel.labelfrontend import mm, inch, px
from pysvglabel.labelfrontend.units import LengthDimension


class UnitsParseTestCase(unittest.TestCase):
    def test_units_parse(self) -> None:
        parsed = LengthDimension.from_str("2 mm")
        self.assertEqual(parsed.value, 2)
        self.assertEqual(parsed.unit, mm)

    def test_units_parse_decimal(self) -> None:
        parsed = LengthDimension.from_str("0.50 mm")
        self.assertEqual(parsed.value, 0.5)
        self.assertEqual(parsed.unit, mm)

    def test_units_parse_spaceless(self) -> None:
        parsed = LengthDimension.from_str("2mm")
        self.assertEqual(parsed.value, 2)
        self.assertEqual(parsed.unit, mm)

    def test_unitless_parse(self) -> None:
        parsed = LengthDimension.from_str("256")
        self.assertEqual(parsed.value, 256)
        self.assertEqual(parsed.unit, px)


class UnitsOpsTestCase(unittest.TestCase):
    def test_add(self) -> None:
        sum = 1.5 * mm + 0.5 * mm
        self.assertEqual(sum.value, 2.0)
        self.assertEqual(sum.unit, mm)

    def test_eq(self) -> None:
        self.assertTrue(1.5 * mm == 1.5 * mm)
        self.assertTrue(0.5 * mm + 1.0 * mm == 1.5 * mm)
        self.assertTrue(1.5 * mm == 0.5 * mm + 1.0 * mm)
        self.assertTrue(1.5 * mm != 0.5 * mm)
        self.assertTrue(25.4 * mm == 1 * inch)

    def test_compare(self) -> None:
        self.assertTrue(1.0 * mm < 1.0 * inch)
        self.assertTrue(1.0 * mm <= 1.0 * inch)
        self.assertTrue(1.0 * inch > 1.0 * mm)
        self.assertTrue(1.0 * inch >= 1.0 * mm)

        self.assertTrue(1.0 * inch >= 25.4 * mm)
        self.assertTrue(1.0 * inch <= 25.4 * mm)
