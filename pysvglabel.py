import argparse
import csv
import xml.etree.ElementTree as ET

from labelcore import SvgTemplate

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Create label sheets from SVG templates.')
  parser.add_argument('template', type=str,
                      help='Input SVG template file.')
  parser.add_argument('csv', type=str,
                      help='Input CSV data file.')
  parser.add_argument('output', type=str,
                      help="Filename to write outputs to. Can have .svg or .pdf extensions."
                           + " If multiple sheets are needed, appends a prefix to the second one, starting with _2.")
  parser.add_argument('--print', type=str,
                      help="Optional printer name, to send output files to a printer as they are generated."
                           + " The output must be a PDF.")
  args = parser.parse_args()

  template = SvgTemplate(args.template)
  template_page_count = template.get_sheet_count()[0] * template.get_sheet_count()[1]

  with open(args.csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    table = [row for row in reader]

  # chunk into page-sized tables
  page_tables = [table[start: start + template_page_count]
                 for start in range(0, len(table), template_page_count)]
  for (page_num, page_table) in enumerate(page_tables):
    page = template.apply_page(page_table)
    filename = args.output
    with open(filename, 'wb') as file:
      root = ET.ElementTree(page)
      root.write(file)

    print(f'Wrote page {page_num + 1}/{len(page_tables)} {filename}')

  # TODO optional PDFing
  # TODO optional printing