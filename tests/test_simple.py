import csv

import xml.etree.ElementTree as ET
from labelcore import SvgTemplate
from LabelTestCase import LabelTestCase


class SimpleLabelTestCase(LabelTestCase):
  def test_simple(self) -> None:
    with open('testdata.csv', newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(ET.parse("test_1.75x0.5.svg"))

    sheets = template.apply_table(table)
    self.write_labels(sheets)
