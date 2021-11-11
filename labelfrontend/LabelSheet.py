from typing import Tuple

from .units import AreaDimension, LengthDimension


class LabelSheet:
  """Label sheet definition specifying a page area and spacing between labels,
  and the labels are centered within the page (so margin spacing is automatically calculated)."""
  def __init__(self, page: AreaDimension, space: AreaDimension, count: Tuple[int, int]):
    self.page = page
    self.space = space
    self.count = count

  def get_margins(self, label_size: Tuple[LengthDimension, LengthDimension]) -> Tuple[LengthDimension, LengthDimension]:
    """Given the sheet of the actual label, returns the X and Y margins."""
    contents_x = (label_size[0] * self.count[0]) + (self.space[0] * (self.count[0] - 1))
    contents_y = (label_size[1] * self.count[1]) + (self.space[1] * (self.count[1] - 1))
    return (self.page[0] - contents_x) / 2, (self.page[1] - contents_y) / 2

  def labels_per_sheet(self) -> int:
    return self.count[0] * self.count[1]
