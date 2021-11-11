from typing import List
import xml.etree.ElementTree as ET
from external.Code128 import code128_widths

from labelcore.GroupReplacer import RectGroupReplacer
from .units import LengthDimension


class Code128(RectGroupReplacer):
  def __init__(self, data: str, thickness: LengthDimension, quiet: bool = True, fill: str = '#000000'):
    assert isinstance(data, str) and isinstance(thickness, LengthDimension)
    self.data = data
    self.thickness = thickness
    self.quiet = quiet
    self.fill = fill

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    height = LengthDimension.from_str(rect.attrib['height'])
    width = LengthDimension.from_str(rect.attrib['width'])

    bar_widths = code128_widths(self.data)
    if self.quiet:
      bar_widths = [10] + bar_widths + [10]

    bar_widths_dim = [self.thickness * width for width in bar_widths]
    total_width = sum(bar_widths_dim)

    output = []
    for bar_widths_dim in bar_widths:
      pass



    return output
