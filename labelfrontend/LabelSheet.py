from typing import Tuple

from .units import AreaDimension, mm


class LabelSheet:
  def __init__(self, page: AreaDimension, space: AreaDimension, count: Tuple[int, int]):
    self.page = page
    self.space = space
    self.count = count
