import unittest

import xml.etree.ElementTree as ET
from typing import List


class LabelTestCase(unittest.TestCase):
  def write_labels(self, sheets: List[ET.Element]) -> None:
    for i, sheet in enumerate(sheets):
      with open(f'out/{self.__class__.__name__}_{self._testMethodName}_{i}.svg', 'wb') as file:
        root = ET.ElementTree(sheet)
        root.write(file)
