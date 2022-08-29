import unittest

import xml.etree.ElementTree as ET
import os.path
import inspect


class LabelTestCase(unittest.TestCase):
  def get_base_dir(self) -> str:
    return os.path.dirname(inspect.getfile(self.__class__))

  def write_label(self, sheet: ET.Element) -> None:
    with open(os.path.join(self.get_base_dir(), 'out', f'{self.__class__.__name__}_{self._testMethodName}.svg'),
              'wb') as file:
      root = ET.ElementTree(sheet)
      root.write(file)
