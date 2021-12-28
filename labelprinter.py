import argparse
import os
import csv
import xml.etree.ElementTree as ET
import time

import win32api
import win32print

from labelcore import SvgTemplate


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Print individual labels (eg, with a thermal printer) from SVG templates.')
  parser.add_argument('printer', type=str,
                      help='Printer name to print to.')
  parser.add_argument('template', type=str,
                      help='Input SVG template file.')
  parser.add_argument('csv', type=str,
                      help='Input CSV data file to monitor for changes on.')
  # TODO: support user-defineable generated filename
  args = parser.parse_args()

  template = SvgTemplate(ET.parse(args.template))


  def canonicalize_row_dict(row_dict):
    # Discard empty cells - to not print everything is a new row is added
    return tuple(sorted([(k, v) for (k, v) in row_dict.items() if v]))


  last_mod_time = None  # None means initial read, and to not print anythign
  last_seen_set = set()
  while True:
    if not os.path.isfile(args.csv):
      print("Warning: file not found")
      continue

    try:
      mod_time = os.path.getmtime(args.csv)
    except FileNotFoundError:
      continue  # sometimes the file temporarily disappears, just ignore it
    if mod_time == last_mod_time:  # file unchanged, ignore
      continue

    time.sleep(0.25)  # TODO HACK: wait for the file the stabilize

    with open(args.csv, 'r') as csvfile:
      print("File modification detected")
      reader = csv.DictReader(csvfile)
      seen_set = set()
      all_row_dicts = list(reader)
      for row_index, row_dict in enumerate(all_row_dicts):
        row_set = canonicalize_row_dict(row_dict)
        seen_set.add(row_set)
        if row_set not in last_seen_set and last_mod_time is not None:
          instance = template.apply_instance(row_dict, all_row_dicts, row_index)
          root = ET.ElementTree(instance)
          root.write("temp.svg")

          print(f"Printing: {row_dict}")

        seen_set.add(row_set)

      last_mod_time = mod_time
      last_seen_set = seen_set

    time.sleep(0.25)
