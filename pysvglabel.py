import argparse
import csv

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

  reader = csv.DictReader(args.csv)
  template = SvgTemplate(args.template)


