import csv

import os.path
from labelcore import SvgTemplate, NAMESPACES
from .LabelTestCase import LabelTestCase


class SubArrayTestCase(LabelTestCase):
  def test_subarray(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_subarray.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_subarray.svg"))

    sheet = self.create_sheet(template, table)
    self.write_label(sheet)
