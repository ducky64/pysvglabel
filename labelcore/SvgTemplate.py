import os.path
import xml.etree.ElementTree as ET
from copy import deepcopy, copy
from typing import Any, Dict, Callable, cast, List, Tuple

from labelfrontend import LabelSheet
from labelfrontend.units import LengthDimension
from .GroupReplacer import GroupReplacer
from .common import BadTemplateException, SVG_NAMESPACE, NAMESPACES, SVG_GRAPHICS_TAGS


def get_text_of(elt: ET.Element) -> str:
  inner_texts = [get_text_of(child) for child in get_text_inner_elts(elt)]
  return (elt.text or "") + "".join(inner_texts)


def get_text_child_elts(elt: ET.Element) -> List[ET.Element]:
  return [child for child in elt
          if child.tag in (
            f'{SVG_NAMESPACE}text',
            f'{SVG_NAMESPACE}flowRoot',
          )]


def get_text_inner_elts(elt: ET.Element) -> List[ET.Element]:
  return [child for child in elt
          if child.tag in (
            f'{SVG_NAMESPACE}tspan',
            f'{SVG_NAMESPACE}flowPara',
          )]


def visit(elt: ET.Element, fn: Callable[[ET.Element], None]) -> None:
  fn(elt)
  for child in elt.findall('svg:g', NAMESPACES):
    visit(child, fn)


class SvgTemplate:
  def __init__(self, filename: str):
    self.file_abspath = os.path.abspath(filename)
    root = ET.parse(filename)
    self.env: Dict[str, Any] = cast(Any, None)
    self.sheet: LabelSheet = cast(Any, None)
    self.size: Tuple[LengthDimension, LengthDimension]

    def replace_start(elt: ET.Element) -> None:
      for child in get_text_child_elts(elt):
        child_text = get_text_of(child)
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

    newroot = deepcopy(root.getroot())

    visit(newroot, replace_start)
    if self.env is None:
      raise BadTemplateException("no starting blocks (textboxes starting with 🏁) found")
    if self.sheet is None:
      raise BadTemplateException("no sheet defined")

    if 'width' not in newroot.attrib:
      raise BadTemplateException("svg missing width")
    if 'height' not in newroot.attrib:
      raise BadTemplateException("svg missing height")
    self.size = (LengthDimension.from_str(newroot.attrib['width']),
                 LengthDimension.from_str(newroot.attrib['height']))

    # split the combined SVG into a skeleton and template elements
    self.template_elts = []
    self.skeleton = newroot
    for child in self.skeleton:
      if child.tag in SVG_GRAPHICS_TAGS:
        self.template_elts.append(deepcopy(child))
        self.skeleton.remove(child)

  def get_sheet_count(self) -> Tuple[int, int]:
    return self.sheet.count

  def _create_instance(self) -> ET.Element:
    """Creates the top-level SVG object for a single label."""
    return deepcopy(self.skeleton)

  def _create_sheet(self) -> ET.Element:
    """Creates the top-level SVG object for a sheet.
    TODO - separate responsibilities with create_single? perhaps sheets should be a different object entirely?
    """
    top = deepcopy(self.skeleton)
    top.attrib['width'] = self.sheet.page[0].to_str()
    top.attrib['height'] = self.sheet.page[1].to_str()
    if 'viewBox' in top.attrib:
      del top.attrib['viewBox']
    return top

  def apply_instance(self, row: Dict[str, str], table: List[Dict[str, str]], row_num: int) -> ET.Element:
    """Creates a copy of this template, with substitutions for the given row data.
    The env dict is shallow-copied, so variable changes aren't reflected in other rows,
    but mutation effects will be visible."""
    new_root = ET.Element(f'{SVG_NAMESPACE}g')

    env = copy(self.env)
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}  # discard non-identifiers
    env.update(value_variables)
    env.update({'row': row, 'table': table, 'row_num': row_num})

    def process_text(elt: ET.Element) -> None:
      for child in get_text_inner_elts(elt):
        process_text(child)
      if elt.text:
        elt.text = eval(f'f"""{elt.text}"""', env)  # TODO proper escaping, even though """ in a label is unlikely

    def apply_template(elt: ET.Element) -> None:
      text_child_elts = get_text_child_elts(elt)
      command_child_elts = [text_child_elt for text_child_elt in text_child_elts
                            if get_text_of(text_child_elt).startswith('🐍')]

      if len(command_child_elts) == 1:
        command_elt = command_child_elts[0]
        code = get_text_of(command_elt).strip('🐍')
        obj = eval(code, env)
        if not isinstance(obj, GroupReplacer):
          raise BadTemplateException(f'🐍 textbox expected result of type GroupReplacer, got {type(obj)}, in {code}')

        elt.remove(command_elt)
        new_elts = obj.process_group(self, list(elt))
        for child in list(elt):  # elt.clear also deletes attribs
          elt.remove(child)
        elt.extend(new_elts)
      elif len(command_child_elts) > 1:
        raise BadTemplateException('cannot have multiple 🐍 textboxes in the same group')
      else:
        for child in text_child_elts:
          process_text(child)

    for elt in self.template_elts:
      new_elt = deepcopy(elt)
      visit(new_elt, apply_template)
      new_root.append(new_elt)
    return new_root

  def apply_page(self, table: List[Dict[str, str]]) -> ET.Element:
    """Given a table containing at most one page's worth of entries, creates a page of labels.
    If there are less entries than a full page, returns a partial page."""
    sheet = self._create_sheet()

    (margin_x, margin_y) = self.sheet.get_margins(self.size)
    for row_num, row in enumerate(table):
      if row_num >= self.sheet.labels_per_sheet():
        raise BadTemplateException(f'table contains more entries than {self.sheet.labels_per_sheet()} per page')

      count_x = row_num % self.sheet.count[0]
      count_y = row_num // self.sheet.count[0]
      offset_x = margin_x + (self.size[0] + self.sheet.space[0]) * count_x
      offset_y = margin_y + (self.size[1] + self.sheet.space[1]) * count_y

      instance = self.apply_instance(row, table, row_num)
      instance.attrib['transform'] = f'translate({offset_x.to_px()}, {offset_y.to_px()})'
      sheet.append(instance)

    return sheet
