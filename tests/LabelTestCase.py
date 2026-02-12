import unittest

import xml.etree.ElementTree as ET
import os
import os.path
import inspect
from typing import Dict, List

from pysvglabel.labelcore import SvgTemplate


class LabelTestCase(unittest.TestCase):
  def get_base_dir(self) -> str:
    return os.path.dirname(inspect.getfile(self.__class__))

  def create_sheet(self, template: SvgTemplate, table: List[Dict[str, str]]) -> ET.Element:
    sheet = template.create_sheet()
    sheet.append(template.apply_page(table))
    return sheet

  def write_label(self, sheet: ET.Element) -> None:
    label_out_dir = os.path.join(self.get_base_dir(), 'out')
    if not os.path.exists(label_out_dir):
      os.makedirs(label_out_dir)
    with open(os.path.join(label_out_dir, f'{self.__class__.__name__}_{self._testMethodName}.svg'),
              'wb') as file:
      root = ET.ElementTree(sheet)
      root.write(file)
