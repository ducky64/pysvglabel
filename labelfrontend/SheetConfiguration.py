from typing import Tuple

from .units import AreaDimension, mm


class SheetConfiguration:
  pass


def configure_sheet(page: AreaDimension, space: AreaDimension = (0, 0)*mm,
                    count: Tuple[int, int] = (1, 1)) -> SheetConfiguration:
  print("Configure sheet")
