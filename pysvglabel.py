import argparse
import csv

from labelcore import SvgTemplate

parser = argparse.ArgumentParser(description='Create label sheets from SVG templates.')
parser.add_argument('template', type=str,
                    help='Input SVG template file.')
parser.add_argument('csv', type=str,
                    help='Input CSV data file.')
parser.add_argument('output', type=str,
                    help="Filename to write outputs to. Must end in .svg."
                         + " If multiple sheets are needed, appends a prefix to the second one, starting with _2."
                         + " (future versions may auto-detect output format by the extension)")
args = parser.parse_args()

reader = csv.DictReader(args.csv)

