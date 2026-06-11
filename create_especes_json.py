import csv
import json

mapping = {}

with open(
    r"C:\Users\pablo\Downloads\species_taxonomy_with_ott.csv",
    encoding="utf-8"
) as f:
    reader = csv.DictReader(f)

    for row in reader:
        mapping[row["NCBI Tax ID"]] = row["Nom commun"]

with open(
    "static/especes.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mapping,
        f,
        ensure_ascii=False,
        indent=4
    )

print("especes.json créé")