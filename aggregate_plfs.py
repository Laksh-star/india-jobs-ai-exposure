"""Aggregate PLFS-style person-level data to NCO 2004 3-digit groups.

Expected CSV columns:
- nco_2004_code
- person_weight
- monthly_earnings_inr
- education_bucket
- rural_urban
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict

from india_pipeline import PROCESSED_DIR, ensure_dirs, normalized_seed_records


def weighted_median(pairs: list[tuple[float, float]]) -> int | None:
    filtered = sorted((value, weight) for value, weight in pairs if value >= 0 and weight > 0)
    if not filtered:
        return None
    total = sum(weight for _, weight in filtered)
    halfway = total / 2
    running = 0.0
    for value, weight in filtered:
        running += weight
        if running >= halfway:
            return int(round(value))
    return int(round(filtered[-1][0]))


def aggregate_from_csv(path: str) -> list[dict[str, object]]:
    workers = defaultdict(float)
    earnings = defaultdict(list)
    education = defaultdict(lambda: defaultdict(float))
    rural_urban = defaultdict(lambda: defaultdict(float))

    with open(path) as handle:
        for row in csv.DictReader(handle):
            code = row["nco_2004_code"].strip()[:3]
            weight = float(row["person_weight"] or 0)
            if not code or weight <= 0:
                continue
            workers[code] += weight

            earnings_value = row.get("monthly_earnings_inr", "").strip()
            if earnings_value:
                earnings[code].append((float(earnings_value), weight))

            education_bucket = row.get("education_bucket", "").strip() or "Unknown"
            education[code][education_bucket] += weight

            region_bucket = row.get("rural_urban", "").strip().lower() or "unknown"
            rural_urban[code][region_bucket] += weight

    total_workers = sum(workers.values()) or 1.0
    payload = []
    for code, worker_count in sorted(workers.items()):
        edu_total = sum(education[code].values()) or 1.0
        region_total = sum(rural_urban[code].values()) or 1.0
        payload.append(
            {
                "nco2004_3d": code,
                "employment_workers": round(worker_count),
                "worker_share": round((worker_count / total_workers) * 100, 4),
                "median_monthly_earnings_inr": weighted_median(earnings[code]),
                "education_mix": {
                    bucket: round((value / edu_total) * 100, 2)
                    for bucket, value in sorted(education[code].items())
                },
                "rural_urban_split": {
                    bucket: round((value / region_total) * 100, 2)
                    for bucket, value in sorted(rural_urban[code].items())
                },
            }
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--seed", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    if args.seed or not args.input:
        payload = [
            {
                "nco2004_3d": record["nco2004_3d"],
                "employment_workers": record["employment_workers"],
                "worker_share": record["worker_share"],
                "median_monthly_earnings_inr": record["median_monthly_earnings_inr"],
                "education_mix": record["education_mix"],
                "rural_urban_split": record["rural_urban_split"],
            }
            for record in normalized_seed_records()
        ]
    else:
        payload = aggregate_from_csv(args.input)

    path = os.path.join(PROCESSED_DIR, "plfs_aggregates.json")
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Wrote {len(payload)} PLFS aggregate rows to {path}")


if __name__ == "__main__":
    main()
