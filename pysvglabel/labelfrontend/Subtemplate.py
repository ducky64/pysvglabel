from typing import List, Optional, Dict, Any
import xml.etree.ElementTree as ET
import os.path

from ..labelcore import SvgTemplate, RectGroupReplacer, SVG_NAMESPACE, SvgTemplateInstance

from .Align import Align
from .Scaling import Scaling
from .Svg import Svg
from .units import LengthDimension


class Subtemplate(RectGroupReplacer):
    """
    Add the contents of a SVG file where this rectangle-area-group is, applying template transforms to the sub-svg.
    """

    def __init__(
        self, filename: Optional[str], env: Dict[str, Any], scaling: Scaling = Scaling.FIT, align: Align = Align.CENTER
    ):
        """
        :param filename: filename of the SVG file to load, if none the element is left empty
        :param env: environment (local variable defined) to apply to the subtemplate
        :param scaling: how to scale the loaded SVG file, whether to drop the SVG as-is or fit into the area
        :param align: how to align the loaded SVG file to the area
        """
        assert isinstance(filename, str) or filename is None
        if filename is not None:
            filename = os.path.abspath(filename)  # take the abspath here to encapsulate working directory
        self.filename = filename
        self.env = env
        self.scaling = scaling
        self.align = align

    def process_rect(self, rect: ET.Element) -> List[ET.Element]:
        if self.filename is None:
            return []

        svg = ET.parse(self.filename).getroot()
        assert svg.tag == f"{SVG_NAMESPACE}svg", f"loaded file {self.filename} root tag is not svg, got {svg.tag}"
        assert "width" in svg.attrib and "height" in svg.attrib, f"loaded svg {self.filename} missing width or height"
        rect_xy = (LengthDimension.from_str(rect.attrib["x"]), LengthDimension.from_str(rect.attrib["y"]))
        rect_wh = (LengthDimension.from_str(rect.attrib["width"]), LengthDimension.from_str(rect.attrib["height"]))

        dirpath = os.path.dirname(self.filename)

        instance_env = SvgTemplate._create_env(os.path.dirname(self.filename))
        instance_env.update(
            {
                "_area_width": rect_wh[0],
                "_area_height": rect_wh[1],
            }
        )
        instance_env.update(self.env)

        svg = SvgTemplateInstance(svg, dirpath).apply_instance(instance_env)

        return [Svg._apply(svg, rect_xy, rect_wh, self.scaling, self.align)]
