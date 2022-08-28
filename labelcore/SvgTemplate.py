import xml.etree.ElementTree as ET
from typing import Any, Dict, Callable, Optional, cast, List, Tuple, OrderedDict
from copy import deepcopy, copy

from labelfrontend import LabelSheet
from labelfrontend.units import LengthDimension
from .common import BadTemplateException, SVG_NAMESPACE, NAMESPACES, SVG_GRAPHICS_TAGS
from .GroupReplacer import GroupReplacer


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
  def __init__(self, root: ET.ElementTree):
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

  def create_single(self) -> ET.Element:
    """Creates the top-level SVG object for a single label."""
    return deepcopy(self.skeleton)

  def create_sheet(self) -> ET.Element:
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

      if len(text_child_elts) == 1 and get_text_of(text_child_elts[0]).startswith('🐍'):
        code = get_text_of(text_child_elts[0]).strip('🐍')
        obj = eval(code, env)
        if not isinstance(obj, GroupReplacer):
          raise BadTemplateException(f'🐍 textbox expected result of type GroupReplacer, got {type(obj)}, in {code}')
        elt.remove(text_child_elts[0])

        new_elts = obj.process_group(list(elt))
        for child in list(elt):  # elt.clear also deletes attribs
          elt.remove(child)
        elt.extend(new_elts)
      else:
        for child in text_child_elts:
          if get_text_of(child).startswith('🐍'):
            raise BadTemplateException('cannot have multiple 🐍 textboxes in the same group')
          process_text(child)

    for elt in self.template_elts:
      new_elt = deepcopy(elt)
      visit(new_elt, apply_template)
      new_root.append(new_elt)
    return new_root

  def apply_table(self, table: List[Dict[str, str]]) -> List[ET.Element]:
    """Given an entire table, generates sheet(s) of labels."""
    sheets = []

    (margin_x, margin_y) = self.sheet.get_margins(self.size)
    for row_num, row in enumerate(table):
      sheet_num = row_num % self.sheet.labels_per_sheet()
      if sheet_num == 0:
        sheets.append(self.create_sheet())

      count_x = sheet_num % self.sheet.count[0]
      count_y = sheet_num // self.sheet.count[0]
      offset_x = margin_x + (self.size[0] + self.sheet.space[0]) * count_x
      offset_y = margin_y + (self.size[1] + self.sheet.space[1]) * count_y

      instance = self.apply_instance(row, table, row_num)
      instance.attrib['transform'] = f'translate({offset_x.to_px()}, {offset_y.to_px()})'
      sheets[-1].append(instance)

    return sheets
