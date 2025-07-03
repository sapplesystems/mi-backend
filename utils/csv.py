import csv


def read_csv(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL)
        all_values = list(reader)
        return all_values
