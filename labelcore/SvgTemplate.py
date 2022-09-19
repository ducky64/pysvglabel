import os.path
import xml.etree.ElementTree as ET
from copy import deepcopy, copy
from typing import Any, Dict, Callable, cast, List, Tuple, TYPE_CHECKING

from .common import BadTemplateException, SVG_NAMESPACE, NAMESPACES, SVG_GRAPHICS_TAGS


def get_text_of(elt: ET.Element) -> str:
  inner_texts = [get_text_of(child) for child in filter_text_inner_elts(list(elt))]
  return (elt.text or "") + "".join(inner_texts)


def filter_text_elts(elts: List[ET.Element]) -> List[ET.Element]:
  return [child for child in elts
          if child.tag in (
            f'{SVG_NAMESPACE}text',
            f'{SVG_NAMESPACE}flowRoot',
          )]


def filter_text_inner_elts(elts: List[ET.Element]) -> List[ET.Element]:
  return [child for child in elts
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
    from labelfrontend import LabelSheet
    from labelfrontend.units import LengthDimension

    self.file_abspath = os.path.abspath(filename)
    self.dir_abspath = os.path.dirname(self.file_abspath)
    root = ET.parse(filename)
    self.env: Dict[str, Any] = cast(Any, None)
    self.sheet: LabelSheet = cast(Any, None)
    self.size: Tuple[LengthDimension, LengthDimension]
    self.row_contents: List[str] = []
    self.end_contents: List[str] = []

    newroot = deepcopy(root.getroot())

    def replace_start(elt: ET.Element) -> None:
      for child in filter_text_elts(list(elt)):
        child_text = get_text_of(child)
        if child_text.startswith('# pysvglabel: init'):
          if self.env is not None:
            raise BadTemplateException("multiple starting blocks (textboxes starting with '# pysvglabel: init') found")
          self.env = {}
          exec("from labelfrontend import *", self.env)
          exec("import sys as __sys", self.env)
          dirpath_escaped = self.dir_abspath.replace('\\', '\\\\')
          exec(f"__sys.path.append('{dirpath_escaped}')", self.env)
          exec(child_text, self.env)

          if 'sheet' not in self.env:
            raise BadTemplateException("sheet not defined in starting block")
          if not isinstance(self.env['sheet'], LabelSheet):
            raise BadTemplateException(f"sheet not instance of LabelSheet, got {self.env['sheet']}")
          self.sheet = cast(LabelSheet, self.env['sheet'])

          elt.remove(child)  # remove the code block from the template

    visit(newroot, replace_start)
    if self.env is None:
      raise BadTemplateException("no starting blocks (textboxes starting with '# pysvglabel: init') found")
    if self.sheet is None:
      raise BadTemplateException("no sheet defined")

    def replace_row(elt: ET.Element) -> None:
      for child in filter_text_elts(list(elt)):
        child_text = get_text_of(child)
        if child_text.startswith('# pysvglabel: row'):
          self.row_contents.append(child_text)
          elt.remove(child)  # remove the code block from the template

    visit(newroot, replace_row)

    def replace_end(elt: ET.Element) -> None:
      for child in filter_text_elts(list(elt)):
        child_text = get_text_of(child)
        if child_text.startswith('# pysvglabel: end'):
          self.end_contents.append(child_text)
          elt.remove(child)  # remove the code block from the template

    visit(newroot, replace_end)

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

  def create_sheet(self) -> ET.Element:
    """Creates the top-level SVG object for a sheet.
    """
    top = deepcopy(self.skeleton)

    # scale viewBox accordingly
    if 'viewBox' in top.attrib and 'width' in top.attrib and 'height' in top.attrib:
      viewbox_scale_x, viewbox_scale_y = self._viewbox_scale()
      viewbox_x = viewbox_scale_x * self.sheet.page[0].to_px()
      viewbox_y = viewbox_scale_y * self.sheet.page[1].to_px()
      top.attrib['viewBox'] = f'0 0 {viewbox_x} {viewbox_y}'

    top.attrib['width'] = self.sheet.page[0].to_str()
    top.attrib['height'] = self.sheet.page[1].to_str()

    return top

  def _viewbox_scale(self) -> Tuple[float, float]:
    """Returns the viewbox scaling, as factor to multiply by to get true units."""
    from labelfrontend.units import LengthDimension
    if 'viewBox' in self.skeleton.attrib and 'width' in self.skeleton.attrib and 'height' in self.skeleton.attrib:
      viewbox_split = self.skeleton.attrib['viewBox'].split(' ')
      assert len(viewbox_split) == 4, f"viewBox must have 4 components, got {self.skeleton.attrib['viewBox']}"
      width = LengthDimension.from_str(self.skeleton.attrib['width'])
      height = LengthDimension.from_str(self.skeleton.attrib['height'])
      assert viewbox_split[0] == '0' and viewbox_split[1] == '0', "TODO support non-zero viewBox origin"
      return float(viewbox_split[2]) / width.to_px(), float(viewbox_split[3]) / height.to_px()
    else:
      return 1.0, 1.0

  def apply_instance(self, row: Dict[str, str], table: List[Dict[str, str]], row_num: int) -> ET.Element:
    """Creates a copy of this template, with substitutions for the given row data.
    The env dict is shallow-copied, so variable changes aren't reflected in other rows,
    but mutation effects will be visible."""
    new_root = ET.Element(f'{SVG_NAMESPACE}g')

    instance_env = copy(self.env)
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}  # discard non-identifiers
    instance_env.update(value_variables)
    instance_env.update({'row': row, 'table': table, 'row_num': row_num})
    for row_code in self.row_contents:
      exec(row_code, instance_env)

    def process_text(elt: ET.Element) -> None:
      for child in filter_text_inner_elts(list(elt)):
        process_text(child)
      if elt.text:
        elt.text = eval(f'f"""{elt.text}"""', instance_env)  # TODO proper escaping, though """ in a label is unlikely
      for child in elt:
        if child.tail:
          child.tail = eval(f'f"""{child.tail}"""', instance_env)  # TODO proper escaping

    def apply_template(elt: ET.Element) -> None:
      from .GroupReplacer import GroupReplacer

      text_child_elts = filter_text_elts(list(elt))
      command_child_elts = [text_child_elt for text_child_elt in text_child_elts
                            if get_text_of(text_child_elt).startswith('🐍')]
      if len(command_child_elts) == 1:
        command_elt = command_child_elts[0]
        code = get_text_of(command_elt).strip('🐍')
        obj = eval(code, instance_env)
        if not isinstance(obj, GroupReplacer):
          raise BadTemplateException(f'🐍 textbox expected result of type GroupReplacer, got {type(obj)}, in {code}')

        elt.remove(command_elt)
        new_elts = obj.process_group(self, list(elt))
        for child in list(elt):  # elt.clear also deletes attribs
          elt.remove(child)
        elt.extend(new_elts)
      elif len(command_child_elts) > 1:
        raise BadTemplateException('cannot have multiple 🐍 textboxes in the same group')

      text_child_elts = filter_text_elts(list(elt))  # make sure to process text on the output of command blocks too
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
    sheet = self.create_sheet()

    (margin_x, margin_y) = self.sheet.get_margins(self.size)
    (viewbox_scale_x, viewbox_scale_y) = self._viewbox_scale()
    for row_num, row in enumerate(table):
      if row_num >= self.sheet.labels_per_sheet():
        raise BadTemplateException(f'table contains more entries than {self.sheet.labels_per_sheet()} per page')

      count_x = row_num % self.sheet.count[0]
      count_y = row_num // self.sheet.count[0]
      if not self.sheet.flip_x:
        offset_x = margin_x + (self.size[0] + self.sheet.space[0]) * count_x
      else:
        offset_x = margin_x + (self.size[0] + self.sheet.space[0]) * (self.sheet.count[0] - 1 - count_x)
      offset_y = margin_y + (self.size[1] + self.sheet.space[1]) * count_y

      instance = self.apply_instance(row, table, row_num)
      assert 'transform' not in instance.attrib
      instance.attrib['transform'] = \
        f'translate({offset_x.to_px() * viewbox_scale_x}, {offset_y.to_px() * viewbox_scale_y})'

      sheet.append(instance)

    return sheet

  def run_end(self) -> None:
    """Call this to run the end block of the template."""
    end_env = copy(self.env)
    for end_code in self.end_contents:
      exec(end_code, end_env)
