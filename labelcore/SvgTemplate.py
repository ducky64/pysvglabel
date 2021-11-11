import xml.etree.ElementTree as ET
from typing import Any, Dict, Callable, Optional, cast, List
from copy import deepcopy, copy

from labelfrontend import LabelSheet


class BadTemplateException(Exception):
  """Base class for all template errors."""
  pass


SVG_NAMESPACE = '{http://www.w3.org/2000/svg}'
NAMESPACES = {
  'svg': 'http://www.w3.org/2000/svg',
}


def text_of(elt: ET.Element) -> str:
  inner_texts = [text_of(child) for child in text_inner_elts(elt)]
  return (elt.text or "") + "".join(inner_texts)


def text_child_elts(elt: ET.Element) -> List[ET.Element]:
  return [child for child in elt
          if child.tag in (
            f'{SVG_NAMESPACE}text',
            f'{SVG_NAMESPACE}flowRoot',
          )]


def text_inner_elts(elt: ET.Element) -> List[ET.Element]:
  return [child for child in elt
          if child.tag in (
            f'{SVG_NAMESPACE}tspan',
            f'{SVG_NAMESPACE}flowPara',
          )]


class SvgTemplate:
  @classmethod
  def _visit(cls, elt: ET.Element, fn: Callable[[ET.Element], None]) -> None:
    fn(elt)
    for child in elt.findall('svg:g', NAMESPACES):
      cls._visit(child, fn)

  def __init__(self, root: ET.ElementTree):
    self.root = root
    self.env: Dict[str, Any] = cast(Any, None)
    self.sheet: LabelSheet = cast(Any, None)

    def replace_start(elt: ET.Element) -> None:
      for child in text_child_elts(elt):
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

    self._visit(self.root.getroot(), replace_start)

    if self.env is None:
      raise BadTemplateException("no starting blocks (textboxes starting with 🏁) found")

  def create_sheet(self) -> ET.Element:
    """Creates the top-level SVG object for a sheet."""
    top = ET.Element(f'{SVG_NAMESPACE}svg')
    top.attrib['width'] = self.sheet.page[0].to_str()
    top.attrib['height'] = self.sheet.page[1].to_str()
    return top

  def apply_instance(self, row: Dict[str, str], table: List[Dict[str, str]], row_num: int) -> ET.Element:
    """Creates a copy of this template, with substitutions for the given row data.
    The env dict is shallow-copied, so variable changes aren't reflected in other rows,
    but mutation effects will be visible."""
    new = deepcopy(self.root.getroot())
    if 'viewBox' in new.attrib:
      del new.attrib['viewBox']

    env = copy(self.env)
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}  # discard non-identifiers
    env.update(value_variables)
    env.update({'row': row, 'table': table, 'row_num': row_num})

    def process_text(elt: ET.Element) -> None:
      for child in text_inner_elts(elt):
        process_text(child)
      if elt.text:
        elt.text = eval(f'f"""{elt.text}"""', env)  # TODO proper escaping, even though """ in a label is unlikely

    def apply_template(elt: ET.Element) -> None:
      for child in text_child_elts(elt):
        if not text_of(child).startswith('🐍'):
          process_text(child)

    self._visit(new, apply_template)
    return new

  def apply_table(self, table: List[Dict[str, str]]) -> List[ET.Element]:
    """Given an entire table, generates sheet(s) of labels."""
    sheets = [self.create_sheet()]
    curr_sheet_num = 0

    for row_num, row in enumerate(table):
      instance = self.apply_instance(row, table, row_num)


    return sheets
