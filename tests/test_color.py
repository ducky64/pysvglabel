import csv

import os.path
from labelcore import SvgTemplate, NAMESPACES
from .LabelTestCase import LabelTestCase


class TextColorTestCase(LabelTestCase):
  def test_text_color(self) -> None:
    with open(os.path.join(self.get_base_dir(), 'test_color.csv'), newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(os.path.join(self.get_base_dir(), "test_color.svg"))

    sheet = self.create_sheet(template, table)
    self.write_label(sheet)

    groups = sheet.findall('svg:g', NAMESPACES)[0].findall('svg:g', NAMESPACES)
    self.assertEqual(len(groups), 6)

    # TODO text_of should add newlines?
    # ignoring type is needed here to avoid boilerplate assertions that find returns not-None
    self.assertIn('fill:#ff0000', groups[0][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
    self.assertIn('fill:#00ff00', groups[1][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
    self.assertIn('fill:#0000ff', groups[2][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
    self.assertIn('fill:#ffff00', groups[3][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
    self.assertIn('fill:#00ffff', groups[4][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore

    self.assertIn('fill:#ff0000', groups[5][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
    self.assertIn('fill-opacity:0', groups[5][0][0].find('svg:flowRoot', NAMESPACES).attrib['style'])  # type: ignore
