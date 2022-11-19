import xml.etree.ElementTree as ET
from typing import List, Dict

from labelcore.SvgTemplate import SvgTemplate
from labelcore.GroupReplacer import GroupReplacer


class StyleModifier(GroupReplacer):
  """
  A generic modifier that changes a style attribute of all elements in the group
  """
  def __init__(self, attribs: Dict[str, str]):
    """
    :param attribs: dict of attrib names to values, eg '{'fill': '#ffffff'}'
    """
    self.attribs = attribs

  def process_group(self, context: SvgTemplate, elts: List[ET.Element]) -> List[ET.Element]:
    for elt in elts:
      if 'style' not in elt.attrib:
        elt.attrib['style'] = ''
      style_contents = elt.attrib['style'].split(';')
      style_pairs = [elt.split(':') for elt in style_contents]
      style_pairs = [elt for elt in style_pairs
                     if elt[0] not in self.attribs.keys()]  # discard existing keys
      for attrib_name, attrib_value in self.attribs.items():
        style_pairs.append([attrib_name, attrib_value])  # and tack new values at the end
      style_contents = [':'.join(elt) for elt in style_pairs]
      elt.attrib['style'] = ';'.join(style_contents)

    return elts


class FillColor(StyleModifier):
  """
  Changes the fill color of objects within this group.
  If the color is specified with transparency (as consistent with the Inkscape color UI),
  this additionally maps the fill-opacity attribute.
  """
  def __init__(self, color: str):
    """
    :param color: new color
    """
    if color.startswith('#') and len(color) == 9:  # need to separately map opacity
      opacity = int(color[8:9], 16)
      super().__init__({'fill': color[:8], 'fill-opacity': str(opacity / 255)})
    else:
      super().__init__({'fill': color})


class StrokeColor(StyleModifier):
  """
  Changes the fill color of objects within this group.
  If the color is specified with transparency (as consistent with the Inkscape color UI),
  this additionally maps the stroke-opacity attribute.
  """
  def __init__(self, color: str):
    """
    :param color: new color
    """
    if color.startswith('#') and len(color) == 9:  # need to separately map opacity
      opacity = int(color[8:9], 16)
      super().__init__({'stroke': color[:8], 'stroke-opacity': str(opacity / 255)})
    else:
      super().__init__({'stroke': color})
