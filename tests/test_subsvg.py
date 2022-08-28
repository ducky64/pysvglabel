import csv

import os.path
import xml.etree.ElementTree as ET
from labelcore import SvgTemplate, NAMESPACES
from .LabelTestCase import LabelTestCase


class SubSvgTestCase(LabelTestCase):
  def test_subsvg(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_subsvg.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_subsvg.svg"))

    sheet = template.apply_page(table)
    self.write_label(sheet)

    groups = sheet.findall('svg:g', NAMESPACES)
    self.assertEqual(len(groups), 5)
