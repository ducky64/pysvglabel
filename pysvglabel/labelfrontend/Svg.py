from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET
import os.path

from ..labelcore import RectGroupReplacer, SVG_NAMESPACE

from .Align import Align
from .Scaling import Scaling
from .units import LengthDimension


class Svg(RectGroupReplacer):
    """
    Add the contents of a SVG file where this rectangle-area-group is.
    """

    def __init__(self, filename: Optional[str], scaling: Scaling = Scaling.FIT, align: Align = Align.CENTER):
        """
        :param filename: filename of the SVG file to load, if none the element is left empty
        :param scaling: how to scale the loaded SVG file, whether to drop the SVG as-is or fit into the area
        :param align: how to align the loaded SVG file to the area
        """
        assert isinstance(filename, str) or filename is None
        if filename is not None:
            filename = os.path.abspath(filename)  # take the abspath here to encapsulate working directory
        self.filename = filename
        self.scaling = scaling
        self.align = align

    @staticmethod
    def _apply(
        sub: ET.Element,
        rect_xy: Tuple[LengthDimension, LengthDimension],
        rect_wh: Tuple[LengthDimension, LengthDimension],
        scaling: Scaling,
        align: Align,
    ) -> ET.Element:
        """given the contents of the sub-svg, return the transformed version to be placed in the rect"""
        svg_width = LengthDimension.from_str(sub.attrib["width"])
        svg_height = LengthDimension.from_str(sub.attrib["height"])

        wscale, hscale = Scaling.to_transform(scaling, (svg_width, svg_height), rect_wh)
        svg_width = svg_width * wscale
        svg_height = svg_height * hscale

        offset_x, offset_y = Align.to_transform(align, (svg_width, svg_height), rect_wh)
        sub_x = rect_xy[0] + offset_x
        sub_y = rect_xy[1] + offset_y

        transformer = ET.Element(f"{SVG_NAMESPACE}g")
        transformer.attrib["transform"] = f"translate({sub_x.to_str()}, {sub_y.to_str()})"
        transformer.append(sub)
        if (wscale, hscale) != (1.0, 1.0):
            transformer.attrib["transform"] += f" scale({wscale}, {hscale})"
        return transformer

    def process_rect(self, rect: ET.Element) -> List[ET.Element]:
        if self.filename is None:
            return []

        svg = ET.parse(self.filename).getroot()
        assert svg.tag == f"{SVG_NAMESPACE}svg", f"loaded file {self.filename} root tag is not svg, got {svg.tag}"
        assert "width" in svg.attrib and "height" in svg.attrib, f"loaded svg {self.filename} missing width or height"
        rect_xy = (LengthDimension.from_str(rect.attrib["x"]), LengthDimension.from_str(rect.attrib["y"]))
        rect_wh = (LengthDimension.from_str(rect.attrib["width"]), LengthDimension.from_str(rect.attrib["height"]))
        return [self._apply(svg, rect_xy, rect_wh, self.scaling, self.align)]
