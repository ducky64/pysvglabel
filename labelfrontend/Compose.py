import xml.etree.ElementTree as ET
from typing import List

from labelcore.GroupReplacer import GroupReplacer


class Compose(GroupReplacer):
  """
  A modifier that invokes multiple sub-modifiers on the same objects, in sequence.
  """
  def __init__(self, *replacers: GroupReplacer):
    """
    :param replacers: list of sub-replacers to run
    """
    self.replacers = replacers

  def process_group(self, elts: List[ET.Element]) -> List[ET.Element]:
    for replacer in self.replacers:
      elts = replacer.process_group(elts)

    return elts