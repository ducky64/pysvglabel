import csv

import xml.etree.ElementTree as ET
from labelcore import SvgTemplate, NAMESPACES
from labelcore.SvgTemplate import get_text_of
from LabelTestCase import LabelTestCase


class SimpleLabelTestCase(LabelTestCase):
  def test_simple(self) -> None:
    with open('test_simple.csv', newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      table = [row for row in reader]
    template = SvgTemplate(ET.parse("simple_1.75x0.5.svg"))

    sheets = template.apply_table(table)
    self.write_labels(sheets)

    self.assertEqual(len(sheets), 1)
    groups = sheets[0].findall('svg:g', NAMESPACES)
    self.assertEqual(len(groups), 5)

    # TODO text_of should add newlines?
    # ignoring type is needed here to avoid boilerplate assertions that find returns not-None
    self.assertEqual(get_text_of(groups[0][0].find('svg:flowRoot', NAMESPACES)), 'B000 = zeroa')  # type: ignore
    self.assertEqual(get_text_of(groups[1][0].find('svg:flowRoot', NAMESPACES)), 'B011 = oneb')  # type: ignore
    self.assertEqual(get_text_of(groups[2][0].find('svg:flowRoot', NAMESPACES)), 'B022 = twoc')  # type: ignore
    self.assertEqual(get_text_of(groups[3][0].find('svg:flowRoot', NAMESPACES)), 'B033 = threed')  # type: ignore
    self.assertEqual(get_text_of(groups[4][0].find('svg:flowRoot', NAMESPACES)), 'B044 = foure')  # type: ignore
