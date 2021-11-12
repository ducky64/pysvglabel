import csv

import xml.etree.ElementTree as ET
from labelcore import SvgTemplate, NAMESPACES
from labelcore.SvgTemplate import get_text_of
from LabelTestCase import LabelTestCase


class SubSvgTestCase(LabelTestCase):
  def test_simple(self) -> None:
    with open('test_subsvg.csv', newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(ET.parse("test_subsvg.svg"))

    sheets = template.apply_table(table)
    self.write_labels(sheets)

    self.assertEqual(len(sheets), 1)
    groups = sheets[0].findall('svg:g', NAMESPACES)
    self.assertEqual(len(groups), 5)
