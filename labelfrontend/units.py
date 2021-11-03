from typing import Tuple, overload, Union


class LengthDimension:
  raise NotImplementedError


class LengthUnit:
  """Defines a unit of length, which a number can be multiplied by to provide a length dimension."""
  def __init__(self, svg_units: str, pixels: float):
    self.svg_units = svg_units
    self.pixels = pixels

  @overload
  def __rmul__(self, other: float) -> LengthDimension: ...
  @overload
  def __rmul__(self, other: Tuple[float, float]) -> Tuple[LengthDimension, LengthDimension]: ...

  def __rmul__(self, other: Union[float, Tuple[float, float]]) -> \
      Union[LengthDimension, Tuple[LengthDimension, LengthDimension]]:
    raise NotImplementedError


inch = LengthUnit('in', 96)  # in is a reserved keyword

mm = LengthUnit('mm', 96/25.4)
cm = LengthUnit('cm', 96/2.5)

pt = LengthUnit('pt', 96/72)
