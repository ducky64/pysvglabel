from typing import List, cast
import xml.etree.ElementTree as ET

from labelcore import SvgTemplate
from .external.Code128 import code128_widths

from labelcore.GroupReplacer import RectGroupReplacer
from .units import LengthDimension, px


class Code128(RectGroupReplacer):
  """
  Adds a Code 128 barcode where this rectangle-area-group is.
  The barcode height is determined by the rectangle height.
  """
  def __init__(self, data: str, thickness: LengthDimension, quiet: bool = True, fill: str = '#000000'):
    """
    :param data: data of the barcode
    :param thickness: width of a 'module'
    :param quiet: whether to generate the quiet zone
    :param fill: fill color of the bars
    """
    assert isinstance(data, str) and isinstance(thickness, LengthDimension)
    self.data = data
    self.thickness = thickness
    self.quiet = quiet
    self.fill = fill

  def process_rect(self, context: SvgTemplate, rect: ET.Element) -> List[ET.Element]:
    x = LengthDimension.from_str(rect.attrib['x'])
    width = LengthDimension.from_str(rect.attrib['width'])

    bar_widths = code128_widths(self.data)
    # first bar is a dummy spacer, alternate spaces and drawn bars
    if self.quiet:
      bar_widths = [10] + bar_widths + [10]
    else:
      bar_widths = [0] + bar_widths + [0]

    bar_widths_dim = [self.thickness * width for width in bar_widths]
    total_width = cast(LengthDimension, sum(bar_widths_dim, 0 * px))
    assert total_width <= width, f"barcode '{self.data}' width {total_width.to_str()} >= allocated {width.to_str()}"

    output = []
    curr_x = x + (width - total_width) / 2  # center the barcode
    for i, bar_width_dim in enumerate(bar_widths_dim):
      if i % 2 == 1:  # every other entry is a drawn bar
        output.append(ET.Element('rect', {
          'x': curr_x.to_str(),
          'width': bar_width_dim.to_str(),
          'y': rect.attrib['y'],
          'height': rect.attrib['height'],
          'style': f'stroke:none;fill:{self.fill};fill-opacity:1',
        }))
      curr_x += bar_width_dim

    return output
