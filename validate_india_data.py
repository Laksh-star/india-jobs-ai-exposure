"""Validate the India site payload and generated source files."""

from __future__ import annotations

import json
import os
import sys

from india_pipeline import OCCUPATIONS_CSV, OCCUPATIONS_JSON, PROCESSED_DIR, SCORES_JSON


REQUIRED_SITE_FIELDS = {
    "country",
    "title",
    "slug",
    "category",
    "nco2004_3d",
    "nco2015_3d",
    "employment_workers",
    "worker_share",
    "median_monthly_earnings_inr",
    "demand_index",
    "vacancies_90d",
    "exposure",
    "exposure_confidence",
    "education_mix",
    "rural_urban_split",
    "sources",
}


def fail(message: str) -> None:
    print(message)
    sys.exit(1)


def main() -> None:
    for path in (
        OCCUPATIONS_JSON,
        OCCUPATIONS_CSV,
        SCORES_JSON,
        os.path.join(PROCESSED_DIR, "occupation_packets.json"),
        os.path.join("site", "data.json"),
    ):
        if not os.path.exists(path):
            fail(f"Missing required file: {path}")

    with open(os.path.join("site", "data.json")) as handle:
        records = json.load(handle)
    if not records:
        fail("site/data.json is empty")

    for record in records:
        missing = REQUIRED_SITE_FIELDS - set(record)
        if missing:
            fail(f"Missing fields in site record {record.get('title')}: {sorted(missing)}")
        if record["country"] != "India":
            fail(f"Unexpected country in site record: {record['country']}")
        if not isinstance(record["sources"], list) or not record["sources"]:
            fail(f"Record {record['title']} has no sources")
        if record["employment_workers"] <= 0:
            fail(f"Record {record['title']} has non-positive employment")

    print(f"Validated {len(records)} India site records.")


if __name__ == "__main__":
    main()
