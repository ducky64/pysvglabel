import csv

import os.path
from pysvglabel.labelcore import SvgTemplate
from .LabelTestCase import LabelTestCase


class BarcodeTestCase(LabelTestCase):
  """This doesn't have any way of validating the barcode output, but it at least ensures they don't crash"""
  def test_barcode(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_simple.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_barcode.svg"))

    sheet = self.create_sheet(template, table)
    self.write_label(sheet)
