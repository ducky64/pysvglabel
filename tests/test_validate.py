import csv

import os.path
from labelcore import SvgTemplate, NAMESPACES
from .LabelTestCase import LabelTestCase


class SubValidationTestCase(LabelTestCase):
  def test_validate_ok(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_simple.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_validate.svg"))

    sheet = template.apply_page(table)
    self.write_label(sheet)

  def test_validate_fail(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_simple_empty.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_validate.svg"))

    with self.assertRaises(AssertionError):
      template.apply_page(table)
