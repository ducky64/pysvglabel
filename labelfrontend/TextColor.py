import xml.etree.ElementTree as ET
from typing import List

from labelcore import SvgTemplate, filter_text_elts
from labelcore.GroupReplacer import GroupReplacer


class TextColor(GroupReplacer):
  """
  Changes the text color of other text objects within this group.
  """
  def __init__(self, color: str):
    """
    :param color: new color of the text
    """
    self.color = color

  def process_group(self, context: SvgTemplate, elts: List[ET.Element]) -> List[ET.Element]:
    for elt in filter_text_elts(elts):
      if 'style' not in elt.attrib:
        elt.attrib['style'] = ''
      style_contents = elt.attrib['style'].split(';')
      style_contents = [elt for elt in style_contents  # discard any existing fill styles
                        if not elt.startswith('fill:')]
      style_contents.append(f'fill:{self.color}')  # and tack new fill style onto the end
      elt.attrib['style'] = ';'.join(style_contents)

    return elts
