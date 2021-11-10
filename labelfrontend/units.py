from typing import Tuple, overload, Union


class LengthDimension:
  def __init__(self, value: float, unit: 'LengthUnit'):
    self.value = value
    self.unit = unit

  def to_str(self) -> str:
    return f"{self.value} {self.unit.svg_unit}"


AreaDimension = Tuple[LengthDimension, LengthDimension]


class LengthUnit:
  """Defines a unit of length, which a number can be multiplied by to provide a length dimension."""
  def __init__(self, svg_unit: str, pixels: float):
    self.svg_unit = svg_unit
    self.pixels = pixels

  @overload
  def __rmul__(self, other: float) -> LengthDimension: ...
  @overload
  def __rmul__(self, other: Tuple[float, float]) -> AreaDimension: ...

  def __rmul__(self, other: Union[float, Tuple[float, float]]) -> \
      Union[LengthDimension, AreaDimension]:
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
