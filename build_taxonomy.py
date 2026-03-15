"""Build the canonical India occupation taxonomy.

By default this writes the bundled seed taxonomy. If a CSV is provided, it
must contain: nco2004_3d,title,nco2015_3d,category
"""

import argparse
import csv
import json
import os

from india_pipeline import PROCESSED_DIR, ensure_dirs, normalized_seed_records, slugify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-csv", default=None)
    args = parser.parse_args()

    ensure_dirs()
    records = []
    if args.from_csv:
        with open(args.from_csv) as handle:
            for row in csv.DictReader(handle):
                records.append(
                    {
                        "title": row["title"],
                        "slug": f"{row['nco2004_3d']}-{slugify(row['title'])}",
                        "country": "India",
                        "nco2004_3d": row["nco2004_3d"],
                        "nco2015_3d": row["nco2015_3d"],
                        "category": row["category"],
                    }
                )
    else:
        for row in normalized_seed_records():
            records.append(
                {
                    "title": row["title"],
                    "slug": row["slug"],
                    "country": row["country"],
                    "nco2004_3d": row["nco2004_3d"],
                    "nco2015_3d": row["nco2015_3d"],
                    "category": row["category"],
                }
            )

    path = os.path.join(PROCESSED_DIR, "taxonomy.json")
    with open(path, "w") as handle:
        json.dump(records, handle, indent=2)
    print(f"Wrote {len(records)} taxonomy rows to {path}")


if __name__ == "__main__":
    main()
