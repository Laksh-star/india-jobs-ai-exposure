"""Build the static site payload for the India labour-market view."""

from __future__ import annotations

import csv
import json
import os


def main() -> None:
    with open("scores.json") as handle:
        scores = {row["nco2004_3d"]: row for row in json.load(handle)}

    data = []
    with open("occupations.csv") as handle:
        for row in csv.DictReader(handle):
            score = scores.get(row["nco2004_3d"], {})
            data.append(
                {
                    "country": row["country"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "category": row["category"],
                    "nco2004_3d": row["nco2004_3d"],
                    "nco2015_3d": row["nco2015_3d"],
                    "employment_workers": int(row["employment_workers"]),
                    "worker_share": float(row["worker_share"]),
                    "median_monthly_earnings_inr": int(row["median_monthly_earnings_inr"]),
                    "median_annual_earnings_inr": int(row["median_annual_earnings_inr"]),
                    "plfs_pay_confidence": row["plfs_pay_confidence"],
                    "employment_confidence": row["employment_confidence"],
                    "vacancies_90d": int(row["vacancies_90d"]),
                    "demand_index": int(row["demand_index"]),
                    "demand_confidence": row["demand_confidence"],
                    "education_mix": json.loads(row["education_mix_json"]),
                    "rural_urban_split": json.loads(row["rural_urban_split_json"]),
                    "sources": json.loads(row["sources_json"]),
                    "description_source": row["description_source"],
                    "postings_source": row["postings_source"],
                    "exposure": score.get("exposure"),
                    "exposure_confidence": score.get("exposure_confidence"),
                    "exposure_rationale": score.get("rationale"),
                    "evidence_sources": score.get("evidence_sources", []),
                    "url": row["url"],
                }
            )

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as handle:
        json.dump(data, handle)

    total_workers = sum(record["employment_workers"] for record in data)
    print(f"Wrote {len(data)} occupations to site/data.json")
    print(f"Total workers represented: {total_workers:,}")


if __name__ == "__main__":
    main()
