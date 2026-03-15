"""Build occupation packets and markdown pages for the India dataset."""

import argparse
import json
import os

from india_pipeline import PROCESSED_DIR, normalized_seed_records, write_occupations_json, write_packets_json, write_pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Build India occupation packets")
    parser.add_argument("--input", default=None, help="Optional prebuilt packet JSON")
    parser.add_argument("--seed", action="store_true", help="Force the bundled India seed dataset")
    args = parser.parse_args()

    if args.input and not args.seed:
        with open(args.input) as handle:
            records = json.load(handle)
    else:
        records = normalized_seed_records()

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    write_packets_json(records)
    write_pages(records)
    write_occupations_json(records)
    print(f"Wrote {len(records)} occupation packets and markdown pages.")


if __name__ == "__main__":
    main()
