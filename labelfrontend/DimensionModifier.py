import xml.etree.ElementTree as ET
from typing import List, Dict

from labelcore import SvgTemplate
from labelcore.GroupReplacer import GroupReplacer
from labelfrontend.units import LengthDimension


class DimensionModifier(GroupReplacer):
  """
  A generic modifier that modifies length attributes
  """
  def __init__(self, attribs: Dict[str, LengthDimension]):
    """
    :param attribs: dict of attrib names to values, eg '{'fill': 10*mm}'
    """
    self.attribs = attribs

  def process_group(self, context: SvgTemplate, elts: List[ET.Element]) -> List[ET.Element]:
    for elt in elts:
      for attrib_name, attrib_value in self.attribs.items():
        assert attrib_name in elt.attrib, f"attrib {attrib_name} missing from elt"
        elt.attrib[attrib_name] = str(attrib_value.to_px())

    return elts
