import argparse
import csv


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Interactively adds rows to a CSV file with an incrementing ID field.')
  # TODO needs a lot more documentation
  parser.add_argument('csv', type=str,
                      help='filename of the CSV.')
  parser.add_argument('id', type=str, nargs='?',
                      help='row name of the ID field.',
                      default="barcode")
  parser.add_argument('id_len', type=int, nargs='?',
                      help='digits in the id field.',
                      default=4)
  parser.add_argument('format', type=str, nargs='?',
                      help='format of rows to add to, separated by semicolons.',
                      default='description;details')
  args = parser.parse_args()

  with open(args.csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    assert reader.fieldnames is not None
    id_index = reader.fieldnames.index(args.id)
    format_elts = args.format.split(';')
    format_index = [reader.fieldnames.index(elt) for elt in format_elts]

    last_index = -1

    for row_index, row_dict in enumerate(list(reader)):
      if args.id in row_dict:
        last_index = max(last_index, int(row_dict[args.id]))

  print(f"last index: {last_index}")

  with open(args.csv, 'a') as csvfile:
    writer = csv.writer(csvfile, lineterminator='\n')
    while True:
      last_index += 1
      row_data = [''] * len(reader.fieldnames)
      row_data[id_index] = str(last_index).rjust(args.id_len, '0')

      user_in = input()
      for user_elt_index, user_elt in enumerate(user_in.split(';')):
        row_data[format_index[user_elt_index]] = user_elt

      writer.writerow(row_data)
      csvfile.flush()
      print(f"wrote row: {row_data}")
