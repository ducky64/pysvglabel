from enum import Enum
from typing import List, Optional
import xml.etree.ElementTree as ET
import os.path

from labelcore import SvgTemplate, RectGroupReplacer, SVG_NAMESPACE

from .Align import Align
from .units import LengthDimension


class Svg(RectGroupReplacer):
  """
  Add the contents of a SVG file where this rectangle-area-group is.
  """

  class Scaling(Enum):
    NONE = 1,
    FIT = 2,

  def __init__(self, filename: Optional[str], scaling: Scaling = Scaling.FIT, align: Align = Align.CENTER):
    """
    :param filename: filename of the SVG file to load, if none the element is left empty
    :param scaling: how to scale the loaded SVG file, whether to drop the SVG as-is or fit into the area
    """
    assert isinstance(filename, str) or filename is None
    self.filename = filename
    self.scaling = scaling
    self.align = align

  @staticmethod
  def _apply(sub: ET.Element, rect_xy: (float, float), rect_wh: (float, float), scaling: Scaling, align: Align) \
      -> ET.Element:
    """given the contents of the sub-svg, return the transformed version to be placed in the rect"""
    rect_x, rect_y = rect_xy
    rect_width, rect_height = rect_wh
    svg_width = LengthDimension.from_str(sub.attrib['width'])
    svg_height = LengthDimension.from_str(sub.attrib['height'])

    if scaling == Svg.Scaling.NONE:
      scale = 1.0
    elif scaling == Svg.Scaling.FIT:
      width_scale = rect_width.to_px() / svg_width.to_px()
      height_scale = rect_height.to_px() / svg_height.to_px()
      scale = min(width_scale, height_scale)
      svg_width = svg_width * scale
      svg_height = svg_height * scale
    else:
      raise NotImplementedError

    offset_x, offset_y = Align.to_transform(align, (svg_width, svg_height), (rect_width, rect_height))
    sub_x = rect_x + offset_x
    sub_y = rect_y + offset_y

    if scaling == Svg.Scaling.NONE:
      sub.attrib['x'] = sub_x.to_str()
      sub.attrib['y'] = sub_y.to_str()
      return sub
    elif scaling == Svg.Scaling.FIT:
      scaler = ET.Element(f'{SVG_NAMESPACE}g')
      scaler.attrib['transform'] = f"translate({sub_x.to_str()}, {sub_y.to_str()}) scale({scale})"
      scaler.append(sub)
      return scaler
    else:
      raise NotImplementedError

  def process_rect(self, context: SvgTemplate, rect: ET.Element) -> List[ET.Element]:
    if self.filename is None:
      return []

    svg = ET.parse(os.path.join(context.dir_abspath, self.filename)).getroot()
    assert svg.tag == f"{SVG_NAMESPACE}svg", f"loaded file {self.filename} root tag is not svg, got {svg.tag}"
    assert 'width' in svg.attrib and 'height' in svg.attrib, f"loaded svg {self.filename} missing width or height"
    rect_xy = (LengthDimension.from_str(rect.attrib['x']), LengthDimension.from_str(rect.attrib['y']))
    rect_wh = (LengthDimension.from_str(rect.attrib['width']), LengthDimension.from_str(rect.attrib['height']))
    return [self._apply(svg, rect_xy, rect_wh, self.scaling, self.align)]
