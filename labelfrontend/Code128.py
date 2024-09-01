from typing import List, cast
import xml.etree.ElementTree as ET

from .Align import Align
from .external.Code128 import code128_widths

from labelcore.SvgTemplate import SvgTemplate
from labelcore.common import SVG_NAMESPACE
from labelcore.GroupReplacer import RectGroupReplacer
from .units import LengthDimension, px


class Code128(RectGroupReplacer):
  """
  Adds a Code 128 barcode where this rectangle-area-group is.
  The barcode height is determined by the rectangle height.
  """
  def __init__(self, data: str, thickness: LengthDimension, quiet: bool = True,
               align: Align = Align.CENTER, fill: str = '#000000'):
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
    self.align = align
    self.fill = fill

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    bar_widths = code128_widths(self.data)

    if self.quiet:  # first bar is a dummy spacer, alternate spaces and drawn bars
      bar_widths = [10] + bar_widths + [10]
    else:
      bar_widths = [0] + bar_widths + [0]
    total_width = sum(bar_widths)

    x = LengthDimension.from_str(rect.attrib['x'])
    y = LengthDimension.from_str(rect.attrib['y'])
    width = LengthDimension.from_str(rect.attrib['width'])
    height = LengthDimension.from_str(rect.attrib['height'])
    align_x, align_y = Align.to_transform(self.align, (self.thickness * total_width, 0 * px),
                                          (width, 0 * px))
    assert self.thickness * total_width <= width, \
      f"barcode '{self.data}' width {(self.thickness * total_width).to_str()} >= allocated {width.to_str()}"

    path_cmds = ""
    for i, bar_width_dim in enumerate(bar_widths):
      if i % 2 == 1:  # drawn bar
        path_cmds += f"h{bar_width_dim} v1 h{-bar_width_dim} z m{bar_width_dim},0"
      else:  # space
        path_cmds += f"m{bar_width_dim},0"

    return [ET.Element(f'{SVG_NAMESPACE}path', {
      'd': path_cmds,
      'fill': self.fill,
      'stroke': 'transparent',
      'transform': f'translate({(x + align_x).to_str()} {y.to_str()}) scale({self.thickness.to_px()} {height.to_px()})'
    })]
