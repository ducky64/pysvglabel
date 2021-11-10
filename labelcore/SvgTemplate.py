import xml.etree.ElementTree as ET
from typing import Any, Dict, Callable, Optional, cast
from copy import deepcopy

from labelfrontend import LabelSheet


class BadTemplateException(Exception):
  """Base class for all template errors."""
  pass


NAMESPACE = {
  'svg': 'http://www.w3.org/2000/svg',
}


def text_of(elt: ET.Element) -> str:
  subtexts = [text_of(child) for child in elt.findall('svg:tspan', NAMESPACE)]
  return (elt.text or "") + "".join(subtexts)


class SvgTemplate:
  @classmethod
  def visit(cls, elt: ET.Element, fn: Callable[[ET.Element], None]) -> None:
    fn(elt)
    for child in elt.findall('svg:g', NAMESPACE):
      cls.visit(child, fn)

  def __init__(self, root: ET.ElementTree):
    self.root = root
    self.env: Dict[str, Any] = cast(Any, None)
    self.sheet: LabelSheet = cast(Any, None)

    def replace_start(elt: ET.Element) -> None:
      # TODO support flowRoot/flowPara in starting block
      for child in elt.findall('svg:text', NAMESPACE):
        child_text = text_of(child)
        if child_text.startswith('🏁'):
          if self.env is not None:
            raise BadTemplateException("multiple starting blocks (textboxes starting with 🏁) found")
          self.env = {}
          start_code = child_text.strip('🏁')
          exec("from labelfrontend import *", self.env)
          exec(start_code, self.env)

          if 'sheet' not in self.env:
            raise BadTemplateException("sheet not defined in starting block")
          if not isinstance(self.env['sheet'], LabelSheet):
            raise BadTemplateException(f"sheet not instance of LabelSheet, got {self.env['sheet']}")
          self.sheet = cast(LabelSheet, self.env['sheet'])

          elt.remove(child)  # remove the init block from the template

    self.visit(self.root.getroot(), replace_start)

  def create_sheet(self) -> ET.ElementTree:
    raise NotImplementedError

  def apply(self, row: Dict[str, str]) -> ET.Element:
    new = deepcopy(self.root.getroot())
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}
    self.env.update(value_variables)
    self.env.update({'row': row})

    def process_text(elt: ET.Element) -> None:
      for child in elt.findall('svg:tspan', NAMESPACE):
        process_text(child)
      for child in elt.findall('svg:flowPara', NAMESPACE):
        process_text(child)
      if elt.text:
        old_text = elt.text
        elt.text = eval(f'f"""{elt.text}"""', self.env)  # TODO proper escaping, even though """ in a label is unlikely
        print(f"{old_text} -> {elt.text}")

    def apply_template(elt: ET.Element) -> None:
      for child in elt.findall('svg:text', NAMESPACE):
        if not text_of(child).startswith('🐍'):
          process_text(child)
      for child in elt.findall('svg:flowRoot', NAMESPACE):
        if not text_of(child).startswith('🐍'):
          process_text(child)

    self.visit(new, apply_template)

    return new
