import xml.etree.ElementTree as ET
from typing import List

from labelcore import SvgTemplate, filter_text_elts
from labelcore.GroupReplacer import GroupReplacer


class StyleModifier(GroupReplacer):
  """
  A generic modifier that changes a style attribute of all elements in the group
  """
  def __init__(self, attrib_name: str, attrib_value: str):
    """
    :param attrib_name: attribute name, eg 'fill'
    :param attrib_value: attrib value, eg 'ffffff'
    """
    self.attrib_name = attrib_name
    self.attrib_value = attrib_value

  def process_group(self, context: SvgTemplate, elts: List[ET.Element]) -> List[ET.Element]:
    for elt in elts:
      if 'style' not in elt.attrib:
        elt.attrib['style'] = ''
      style_contents = elt.attrib['style'].split(';')
      style_contents = [elt for elt in style_contents  # discard the existing key
                        if not elt.startswith(f'{self.attrib_name}:')]
      style_contents.append(f'{self.attrib_name}:{self.attrib_value}')  # and tack new value at the end
      elt.attrib['style'] = ';'.join(style_contents)

    return elts


class FillColor(StyleModifier):
  """
  Changes the fill color of objects within this group.
  """
  def __init__(self, color: str):
    """
    :param color: new color
    """
    super().__init__('fill', color)


class StrokeColor(StyleModifier):
  """
  Changes the fill color of objects within this group.
  """
  def __init__(self, color: str):
    """
    :param color: new color
    """
    super().__init__('stroke', color)
