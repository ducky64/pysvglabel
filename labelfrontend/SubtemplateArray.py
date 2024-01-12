from typing import List, Optional, Dict, Any, Tuple
import xml.etree.ElementTree as ET
import os.path

from labelcore import SvgTemplate, RectGroupReplacer, SVG_NAMESPACE, SvgTemplateInstance

from .Align import Align
from .Scaling import Scaling
from .Svg import Svg
from .units import LengthDimension


class SubtemplateArray(RectGroupReplacer):
  """
  Instantiate several subtemplates (specified by envs - tuple of pos, env) in a linear array.
  """
  def __init__(self, filename: Optional[str], elts_env: List[Tuple[float, Dict[str, Any]]], vertical: bool = False,
               scaling: Scaling = Scaling.FIT, align: Align = Align.CENTER):
    """
    :param filename: filename of the SVG file to load, if none the element is left empty
    :param elts_env: list of array elements, each as a tuple of (position, env), with position in [0, 1] as a
      fraction of the total area width or height
    :param vertical: whether the subtemplates are arrayed horizontally (false, default) or vertically (true)
    :param scaling: how to scale the loaded SVG file, whether to drop the SVG as-is or fit into the area
    :param align: how to align the loaded SVG file to the area
    """
    assert isinstance(filename, str) or filename is None
    if filename is not None:
      filename = os.path.abspath(filename)  # take the abspath here to encapsulate working directory
    self.filename = filename
    self.elts_env = elts_env
    self.vertical = vertical
    self.scaling = scaling
    self.align = align

  def process_rect(self, rect: ET.Element) -> List[ET.Element]:
    if self.filename is None:
      return []

    svg = ET.parse(self.filename).getroot()
    assert svg.tag == f"{SVG_NAMESPACE}svg", f"loaded file {self.filename} root tag is not svg, got {svg.tag}"
    assert 'width' in svg.attrib and 'height' in svg.attrib, f"loaded svg {self.filename} missing width or height"
    area_xy = (LengthDimension.from_str(rect.attrib['x']), LengthDimension.from_str(rect.attrib['y']))
    area_wh = (LengthDimension.from_str(rect.attrib['width']), LengthDimension.from_str(rect.attrib['height']))

    dirpath = os.path.dirname(self.filename)
    template = SvgTemplateInstance(svg, dirpath)

    outs = []
    for (pos, env) in self.elts_env:
      transformer = ET.Element(f'{SVG_NAMESPACE}g')
      svg = template.apply_instance(self.env)
      if not self.vertical:  # horizontal
        rect_xy = (area_xy[0] + pos * area_wh[0], area_xy[1])
        rect_wh = (0, area_wh[1])
      else:  # vertical
        rect_xy = (area_xy[0], area_xy[1] + pos * area_wh[1])
        rect_wh = (area_wh[0], 0)
      transformer.append(Svg._apply(svg, rect_xy, rect_wh, self.scaling, self.align))
      outs.append(transformer)

    return outs
