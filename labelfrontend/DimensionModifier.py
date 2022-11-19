import xml.etree.ElementTree as ET
from typing import List, Dict

from labelcore.SvgTemplate import SvgTemplate
from labelcore.GroupReplacer import GroupReplacer
from labelfrontend.units import LengthDimension


class DimensionModifier(GroupReplacer):
  """
  A generic modifier that modifies length attributes, allowing both set-to-value and add-to-existing.
  """
  def __init__(self, set: Dict[str, LengthDimension], add: Dict[str, LengthDimension] = {}):
    """
    :param set: dict of attrib names to values to set, eg '{'rx': 10*mm}'
    :param add: dict of attrib names to values to add to the existing value, eg '{'cx': 10*mm}'
    """
    self.set = set
    self.add = add

  def process_group(self, context: SvgTemplate, elts: List[ET.Element]) -> List[ET.Element]:
    for elt in elts:
      for attrib_name, attrib_value in self.set.items():
        assert attrib_name in elt.attrib, f"attrib {attrib_name} missing from elt"
        elt.attrib[attrib_name] = str(attrib_value.to_px())
      for attrib_name, attrib_value in self.add.items():
        assert attrib_name in elt.attrib, f"attrib {attrib_name} missing from elt"
        elt.attrib[attrib_name] = str(float(elt.attrib[attrib_name]) + attrib_value.to_px())

    return elts
