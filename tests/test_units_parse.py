import unittest
from labelfrontend.units import LengthDimension, inch, px


class UnitsParseTestCase(unittest.TestCase):
  def test_units_parse(self) -> None:
    parsed = LengthDimension.from_str('2 in')
    self.assertEqual(parsed.value, 2)
    self.assertEqual(parsed.unit, inch)

  def test_units_parse_decimal(self) -> None:
    parsed = LengthDimension.from_str('0.50 in')
    self.assertEqual(parsed.value, 0.5)
    self.assertEqual(parsed.unit, inch)

  def test_units_parse_spaceless(self) -> None:
    parsed = LengthDimension.from_str('2in')
    self.assertEqual(parsed.value, 2)
    self.assertEqual(parsed.unit, inch)

  def test_unitless_parse(self) -> None:
    parsed = LengthDimension.from_str('256')
    self.assertEqual(parsed.value, 256)
    self.assertEqual(parsed.unit, px)
