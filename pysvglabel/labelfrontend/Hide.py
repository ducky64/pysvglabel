import xml.etree.ElementTree as ET
from typing import List

from ..labelcore.GroupReplacer import GroupReplacer


class Hide(GroupReplacer):
    """
    A generic modifier that deletes its elements if true
    """

    def __init__(self, cond: bool):
        """
        :param cond: hides elements if true, does nothing if false
        """
        self.cond = cond

    def process_group(self, elts: List[ET.Element]) -> List[ET.Element]:
        if self.cond:
            return []
        else:
            return elts
