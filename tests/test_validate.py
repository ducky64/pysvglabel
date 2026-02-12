import csv

import os.path
from pysvglabel.labelcore import SvgTemplate
from .LabelTestCase import LabelTestCase


class ValidationTestCase(LabelTestCase):
    def test_validate_ok(self) -> None:
        with open(os.path.join(self.get_base_dir(), "test_simple.csv"), newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            table = [row for row in reader]
        template = SvgTemplate(os.path.join(self.get_base_dir(), "test_validate.svg"))

        self.create_sheet(template, table)
        template.run_end()

    def test_validate_fail(self) -> None:
        with open(os.path.join(self.get_base_dir(), "test_simple_empty.csv"), newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            table = [row for row in reader]
        template = SvgTemplate(os.path.join(self.get_base_dir(), "test_validate.svg"))

        self.create_sheet(template, table)
        with self.assertRaises(AssertionError):
            template.run_end()
