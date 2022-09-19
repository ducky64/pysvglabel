import argparse
import csv
import xml.etree.ElementTree as ET
import os.path
from typing import Optional

from labelcore import SvgTemplate, InkscapeSubprocess


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create label sheets from SVG templates.')
  parser.add_argument('template', type=str,
                      help='Input SVG template file.')
  parser.add_argument('csv', type=str,
                      help='Input CSV data file.')
  parser.add_argument('output', type=str,
                      help="Filename to write outputs to. Can have .svg or .pdf extensions."
                           + " If multiple sheets are needed, appends a prefix to the second one, starting with _2."
                           + " If PDF output is requested, inkscape must be on the system path.")
  parser.add_argument('--print', type=str,
                      help="Optional printer name, to send output files to a printer as they are generated."
                           + " The output must be a PDF.")
  parser.add_argument('--inkscape_multipage', action='store_true', default=False,
                      help="Use Inkscape's nonstandard multipage functionality, instead of writing multiple files.")
  args = parser.parse_args()

  template = SvgTemplate(args.template)
  template_page_count = template.get_sheet_count()[0] * template.get_sheet_count()[1]

  with open(args.csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    table = [row for row in reader]

  output_name, output_ext = os.path.splitext(args.output)
  inkscape: Optional[InkscapeSubprocess] = None
  if output_ext == '.pdf':
    inkscape = InkscapeSubprocess()

  if args.print:
    import win32api  # type:ignore
    import win32print  # type:ignore
    assert output_ext == '.pdf', "PDF output required to print"

  def write_file(filename: str, sheet: ET.Element) -> None:
    outfiles = []
    with open(filename + '.svg', 'wb') as file:
      root = ET.ElementTree(sheet)
      root.write(file)
      outfiles.append(filename + '.svg')

    if inkscape:
      inkscape.convert(filename + '.svg', filename + '.pdf')
      outfiles.append(filename + '.pdf')

    print(f'Wrote page {page_num + 1}/{len(page_tables)}: {", ".join(outfiles)}')

    if args.print:
      win32api.ShellExecute(0, "print", filename + '.pdf', f'/d:"{args.print}"', ".", 0)
      print(f'Print to {args.print}')

  # chunk into page-sized tables
  page_tables = [table[start: start + template_page_count]
                 for start in range(0, len(table), template_page_count)]

  if args.inkscape_multipage:
    multipage = template.create_sheet()
    namedviews = multipage.findall('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview')
    assert len(namedviews) == 1, f"must have exactly one sodipodi:namedview tag, got {len(namedviews)}"
    namedview = namedviews[0]
    assert len(namedview.findall('{http://www.inkscape.org/namespaces/inkscape}page')) == 0, "namedview must be empty"
    (viewbox_scale_x, viewbox_scale_y) = template._viewbox_scale()

  for (page_num, page_table) in enumerate(page_tables):
    page = template.apply_page(page_table)

    if not args.inkscape_multipage:
      sheet = template.create_sheet()
      sheet.append(page)

      if page_num == 0:
        filename = output_name  # first page doesn't need an extension
      else:
        filename = output_name + f'_{page_num + 1}'
      write_file(filename, sheet)
    else:
      multipage.append(page)
      namedview_page = ET.Element('{http://www.inkscape.org/namespaces/inkscape}page')
      
      namedview.append(namedview_page)

  if args.inkscape_multipage:
    write_file(output_name, multipage)

  template.run_end()

  if inkscape:
    inkscape.close()
