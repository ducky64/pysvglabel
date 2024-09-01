from typing import List
import xml.etree.ElementTree as ET

from labelcore.SvgTemplate import SvgTemplate
from labelcore.GroupReplacer import RectGroupReplacer
from labelcore.common import SVG_NAMESPACE
from .units import LengthDimension
from .Align import Align


class DataMatrix(RectGroupReplacer):
  """
  Adds a DataMatrix 2d barcode where this rectangle-area-group is.
  The pixel size is a parameter.
  This requires the ppf.datamatrix library (https://github.com/adrianschlatter/ppf.datamatrix)
    pip install ppf.datamatrix
  """
  def __init__(self, data: str, size: LengthDimension, align: Align = Align.CENTER, fill: str = '#000000'):
    """
    :param data: data of the barcode
    :param thickness: width of a 'module'
    :param quiet: whether to generate the quiet zone
    :param fill: fill color of the bars
    """
    assert isinstance(data, str) and isinstance(size, LengthDimension)
    self.data = data
    self.size = size
    self.align = align
    self.fill = fill

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    from ppf.datamatrix import DataMatrix  # type: ignore

    datamatrix = DataMatrix(self.data)
    path_cmds = ''.join(datamatrix._svg_path_iterator())
    # last move adds a newline which messes with the bounding box, so delete it
    trailing_newline_index = path_cmds.rfind('m')
    path_cmds = path_cmds[:trailing_newline_index]

    x = LengthDimension.from_str(rect.attrib['x'])
    y = LengthDimension.from_str(rect.attrib['y'])
    width = LengthDimension.from_str(rect.attrib['width'])
    height = LengthDimension.from_str(rect.attrib['height'])
    data_width = len(datamatrix.matrix[0])
    data_height = len(datamatrix.matrix)
    align_x, align_y = Align.to_transform(self.align, (self.size * data_width, self.size * data_height),
                                          (width, height))
    assert self.size * data_width <= width and self.size * data_height < height, \
      f"datamatrix {self.data} with {data_width}x{data_height} matrix overflowed"

    return [ET.Element(f'{SVG_NAMESPACE}path', {
      'd': f"M0,0.5 {path_cmds}",
      'stroke': self.fill,
      'stroke-width': '1',
      'transform': f'translate({(x + align_x).to_str()} {(y + align_y).to_str()}) scale({self.size.to_px()})'
    })]
