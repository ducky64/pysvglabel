import os.path
import xml.etree.ElementTree as ET
from copy import deepcopy, copy
from typing import Any, Dict, Callable, cast, List, Tuple

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
  """Class that defines a SVG sheet template, including init block, per-row blocks, and end block."""
  def __init__(self, filename: str):
    from labelfrontend import LabelSheet
    from labelfrontend.units import LengthDimension

    self.file_abspath = os.path.abspath(filename)
    self.dir_abspath = os.path.dirname(self.file_abspath)
    root = ET.parse(filename)
    self.env: Dict[str, Any] = cast(Any, None)
    self.sheet: LabelSheet = cast(Any, None)
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
          os.chdir(self.dir_abspath)
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

    # split the combined SVG into a skeleton and template elements
    self.skeleton, template = self.split_skeleton_template(newroot)
    self.template = SubTemplate(template, self.dir_abspath)

  def split_skeleton_template(self, root: ET.Element) -> Tuple[ET.Element, ET.Element]:
    """Given a root SVG element, returns a tuple of (skeleton, template) elements.
    The skeleton contains global defs, while the template contains graphical elements.
    Both share the top-level SVG root."""
    skeleton = deepcopy(root)
    template = deepcopy(root)
    skeleton_elts = []
    template_elts = []
    for child in skeleton:
      if child.tag in SVG_GRAPHICS_TAGS:
        template_elts.append(child)
    for child in template_elts:  # separate deletion pass to avoid mutation while traversing
      skeleton.remove(child)

    for child in template:
      if child.tag not in SVG_GRAPHICS_TAGS:
        skeleton_elts.append(child)
    for child in skeleton_elts:  # separate deletion pass to avoid mutation while traversing
      template.remove(child)

    return skeleton, template

  def get_sheet_count(self) -> Tuple[int, int]:
    return self.sheet.count

  def _viewbox_scale(self) -> Tuple[float, float]:
    return self.template._viewbox_scale()

  def _create_instance(self) -> ET.Element:
    """Creates the top-level SVG object for a single label."""
    return deepcopy(self.skeleton)

  def create_sheet(self) -> ET.Element:
    """Creates the top-level SVG object for a sheet.
    """
    top = deepcopy(self.skeleton)

    # scale viewBox accordingly
    if 'viewBox' in top.attrib and 'width' in top.attrib and 'height' in top.attrib:
      viewbox_scale_x, viewbox_scale_y = self.template._viewbox_scale()
      viewbox_x = viewbox_scale_x * self.sheet.page[0].to_px()
      viewbox_y = viewbox_scale_y * self.sheet.page[1].to_px()
      top.attrib['viewBox'] = f'0 0 {viewbox_x} {viewbox_y}'

    top.attrib['width'] = self.sheet.page[0].to_str()
    top.attrib['height'] = self.sheet.page[1].to_str()

    return top

  def apply_instance(self, row: Dict[str, str], table: List[Dict[str, str]], row_num: int) -> ET.Element:
    """Creates a copy of this template, with substitutions for the given row data.
    The env dict is shallow-copied, so variable changes aren't reflected in other rows,
    but mutation effects will be visible."""
    os.chdir(self.dir_abspath)
    instance_env = copy(self.env)
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}  # discard non-identifiers
    instance_env.update(value_variables)
    instance_env.update({'row': row, 'table': table, 'row_num': row_num})
    for row_code in self.row_contents:
      exec(row_code, instance_env)

    instance_env = copy(self.env)
    value_variables = {key: value for key, value in row.items()
                       if key.isidentifier()}  # discard non-identifiers
    instance_env.update(value_variables)
    instance_env.update({'row': row, 'table': table, 'row_num': row_num})

    for row_code in self.row_contents:
      exec(row_code, instance_env)

    return self.template.apply_instance(instance_env)

  def apply_page(self, table: List[Dict[str, str]]) -> ET.Element:
    """Given a table containing at most one page's worth of entries, creates a page of labels.
    If there are less entries than a full page, returns a partial page."""
    new_root = ET.Element(f'{SVG_NAMESPACE}g')

    (margin_x, margin_y) = self.sheet.get_margins(self.template.size)
    (viewbox_scale_x, viewbox_scale_y) = self.template._viewbox_scale()
    for row_num, row in enumerate(table):
      if row_num >= self.sheet.labels_per_sheet():
        raise BadTemplateException(f'table contains more entries than {self.sheet.labels_per_sheet()} per page')

      count_x = row_num % self.sheet.count[0]
      count_y = row_num // self.sheet.count[0]
      if not self.sheet.flip_x:
        offset_x = margin_x + (self.template.size[0] + self.sheet.space[0]) * count_x
      else:
        offset_x = margin_x + (self.template.size[0] + self.sheet.space[0]) * (self.sheet.count[0] - 1 - count_x)
      offset_y = margin_y + (self.template.size[1] + self.sheet.space[1]) * count_y

      instance = self.apply_instance(row, table, row_num)
      assert 'transform' not in instance.attrib
      instance.attrib['transform'] = \
        f'translate({offset_x.to_px() * viewbox_scale_x}, {offset_y.to_px() * viewbox_scale_y})'

      new_root.append(instance)

    return new_root

  def run_end(self) -> None:
    """Call this to run the end block of the template."""
    os.chdir(self.dir_abspath)
    end_env = copy(self.env)
    for end_code in self.end_contents:
      exec(end_code, end_env)


class SubTemplate:
  """Class that defines a SVG template only, excluding top-level data like init block."""
  def __init__(self, template: ET.Element, dir_abspath: str):
    from labelfrontend import LabelSheet
    from labelfrontend.units import LengthDimension

    if 'width' not in template.attrib:
      raise BadTemplateException("svg missing width")
    if 'height' not in template.attrib:
      raise BadTemplateException("svg missing height")
    self.size = (LengthDimension.from_str(template.attrib['width']),
                 LengthDimension.from_str(template.attrib['height']))
    self.dir_abspath = dir_abspath
    self.template = template

  def _viewbox_scale(self) -> Tuple[float, float]:
    """Returns the viewbox scaling, as factor to multiply by to get true units."""
    from labelfrontend.units import LengthDimension
    if 'viewBox' in self.template.attrib and 'width' in self.template.attrib and 'height' in self.template.attrib:
      viewbox_split = self.template.attrib['viewBox'].split(' ')
      assert len(viewbox_split) == 4, f"viewBox must have 4 components, got {self.template.attrib['viewBox']}"
      width = LengthDimension.from_str(self.template.attrib['width'])
      height = LengthDimension.from_str(self.template.attrib['height'])
      assert viewbox_split[0] == '0' and viewbox_split[1] == '0', "TODO support non-zero viewBox origin"
      return float(viewbox_split[2]) / width.to_px(), float(viewbox_split[3]) / height.to_px()
    else:
      return 1.0, 1.0

  def apply_instance(self, env: Dict[str, Any]) -> ET.Element:
    """Creates a copy of this template, with specified environment containing global / local variables."""
    new_root = ET.Element(f'{SVG_NAMESPACE}g')

    def process_text(elt: ET.Element) -> None:
      for child in filter_text_inner_elts(list(elt)):
        process_text(child)
      os.chdir(self.dir_abspath)
      if elt.text:
        elt.text = eval(f'f"""{elt.text}"""', env)  # TODO proper escaping, though """ in a label is unlikely
      for child in elt:
        if child.tail:
          child.tail = eval(f'f"""{child.tail}"""', env)  # TODO proper escaping

    def apply_template(elt: ET.Element) -> None:
      from .GroupReplacer import GroupReplacer

      text_child_elts = filter_text_elts(list(elt))
      command_child_elts = [text_child_elt for text_child_elt in text_child_elts
                            if get_text_of(text_child_elt).startswith('🐍')]
      if len(command_child_elts) == 1:
        command_elt = command_child_elts[0]
        code = get_text_of(command_elt).strip('🐍')
        os.chdir(self.dir_abspath)
        obj = eval(code, env)
        if not isinstance(obj, GroupReplacer):
          raise BadTemplateException(f'🐍 textbox expected result of type GroupReplacer, got {type(obj)}, in {code}')

        elt.remove(command_elt)
        new_elts = obj.process_group(list(elt))
        for child in list(elt):  # elt.clear also deletes attribs
          elt.remove(child)
        elt.extend(new_elts)
      elif len(command_child_elts) > 1:
        raise BadTemplateException('cannot have multiple 🐍 textboxes in the same group')

      text_child_elts = filter_text_elts(list(elt))  # make sure to process text on the output of command blocks too
      for child in text_child_elts:
        process_text(child)

    for child in self.template:
      new_elt = deepcopy(child)
      visit(new_elt, apply_template)
      new_root.append(new_elt)
    return new_root