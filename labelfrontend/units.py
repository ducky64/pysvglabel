from functools import total_ordering
from typing import Tuple, overload, Union, Any
import re


class LengthUnit:
  """Defines a unit of length, which a number can be multiplied by to provide a length dimension."""
  def __init__(self, svg_unit: str, pixels: float):
    self.svg_unit = svg_unit
    self.pixels = pixels

  @overload
  def __rmul__(self, other: float) -> 'LengthDimension': ...
  @overload
  def __rmul__(self, other: Tuple[float, float]) -> 'AreaDimension': ...

  def __rmul__(self, other: Union[float, Tuple[float, float]]) -> \
      Union['LengthDimension', 'AreaDimension']:
    if isinstance(other, (int, float)):
      return LengthDimension(other, self)
    elif isinstance(other, tuple) and len(other) == 2 and \
        isinstance(other[0], (int, float)) and isinstance(other[1], (int, float)):
      return LengthDimension(other[0], self), LengthDimension(other[1], self)
    else:
      raise TypeError(f"bad type to unit multiply, got {other}")


inch = LengthUnit('in', 96)  # in is a reserved keyword

mm = LengthUnit('mm', 96/25.4)
cm = LengthUnit('cm', 96/2.5)

pt = LengthUnit('pt', 96/72)

px = LengthUnit('', 1)


@total_ordering
class LengthDimension:
  STR_TO_UNITS = {
    'in': inch,
    'mm': mm,
    'cm': cm,
    'pt': pt,
  }
  FROM_STR_RE = re.compile(r'^-?(\d+(?:\.\d+)?)\s*([a-zA-Z]*)?$')
  @classmethod
  def from_str(cls, input: str) -> 'LengthDimension':
    match = cls.FROM_STR_RE.match(input)
    assert match, f"can't parse length dimension '{input}'"
    value = float(match.group(1))
    if match.group(2):
      units = cls.STR_TO_UNITS[match.group(2)]
    else:
      units = px
    return value * units

  def __init__(self, value: float, unit: LengthUnit):
    self.value = value
    self.unit = unit

  def to_str(self) -> str:
    return f"{self.value}{self.unit.svg_unit}"

  def to_px(self) -> float:
    return self.value * self.unit.pixels

  def __add__(self, other: 'LengthDimension') -> 'LengthDimension':
    if self.unit != other.unit:  # fall back to pixels
      return LengthDimension(self.to_px() + other.to_px(), px)
    else:
      return LengthDimension(self.value + other.value, self.unit)

  def __sub__(self, other: 'LengthDimension') -> 'LengthDimension':
    if self.unit != other.unit:  # fall back to pixels
      return LengthDimension(self.to_px() - other.to_px(), px)
    else:
      return LengthDimension(self.value - other.value, self.unit)

  def __mul__(self, other: Union[int, float]) -> 'LengthDimension':
    return LengthDimension(self.value * other, self.unit)

  def __truediv__(self, other: Union[int, float]) -> 'LengthDimension':
    return LengthDimension(self.value / other, self.unit)

  def __eq__(self, other: Any) -> bool:
    if isinstance(other, LengthDimension):
      return self.to_px() == other.to_px()
    else:
      return False

  def __lt__(self, other: 'LengthDimension') -> bool:
    return self.to_px() < other.to_px()


AreaDimension = Tuple[LengthDimension, LengthDimension]
