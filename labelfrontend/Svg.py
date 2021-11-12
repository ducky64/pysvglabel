from enum import Enum
from typing import List
import xml.etree.ElementTree as ET

from labelcore.GroupReplacer import RectGroupReplacer
from labelcore.common import SVG_NAMESPACE
from .units import LengthDimension


class Svg(RectGroupReplacer):
  class Scaling(Enum):
    NONE = 1,
    FIT = 2,

  def __init__(self, filename: str, scaling: Scaling = Scaling.FIT):
    assert isinstance(filename, str)
    self.filename = filename
    self.scaling = scaling

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    svg = ET.parse(self.filename).getroot()
    assert svg.tag == f"{SVG_NAMESPACE}svg", f"loaded file {self.filename} root tag is not svg, got {svg.tag}"
    assert 'width' in svg.attrib and 'height' in svg.attrib, f"loaded svg {self.filename} missing width or height"

    rect_x = LengthDimension.from_str(rect.attrib['x'])
    rect_y = LengthDimension.from_str(rect.attrib['y'])
    rect_width = LengthDimension.from_str(rect.attrib['width'])
    rect_height = LengthDimension.from_str(rect.attrib['height'])

    svg_width = LengthDimension.from_str(svg.attrib['width'])
    svg_height = LengthDimension.from_str(svg.attrib['height'])

    if self.scaling == Svg.Scaling.NONE:
      scale = 1
    elif self.scaling == Svg.Scaling.FIT:
      width_scale = rect_width.to_px() / svg_width.to_px()
      height_scale = rect_height.to_px() / svg_height.to_px()
      scale = min(width_scale, height_scale)
    else:
      raise NotImplementedError

    offset_x = rect_x + (rect_width - svg_width * scale) / 2
    offset_y = rect_y + (rect_height - svg_height * scale) / 2

    if self.scaling == Svg.Scaling.NONE:
      svg.attrib['x'] = offset_x.to_str()
      svg.attrib['y'] = offset_y.to_str()

      return [svg]
    elif self.scaling == Svg.Scaling.FIT:

      scaler = ET.Element(f'{SVG_NAMESPACE}g')
      scaler.attrib['transform'] = f"translate({offset_x.to_str()}, {offset_y.to_str()}) scale({scale})"
      scaler.append(svg)

      return [scaler]
