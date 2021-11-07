import unittest

import xml.etree.ElementTree as ET
from labelcore import SvgTemplate


class SimpleLabelTestCase(unittest.TestCase):
  def test_simple(self) -> None:
    template = SvgTemplate(ET.parse("test_1.75x0.5.svg"))
