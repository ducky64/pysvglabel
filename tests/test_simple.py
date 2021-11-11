import unittest
import csv

import xml.etree.ElementTree as ET
from labelcore import SvgTemplate


class SimpleLabelTestCase(unittest.TestCase):
  def test_simple(self) -> None:
    with open('testdata.csv', newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(ET.parse("test_1.75x0.5.svg"))

    tpi = template.apply_instance(table[0], table, 0)

    sheets = template.apply_table(table)
    for i, sheet in enumerate(sheets):
      with open(f'out/{self.__class__.__name__}_{self._testMethodName}_{i}.svg', 'wb') as file:
        root = ET.ElementTree(sheet)
        root.write(file)
