"""Generate prompt.md for the India labour-market dataset."""

from __future__ import annotations

import csv
import json


def fmt_workers(workers: int | None) -> str:
    if workers is None:
        return "?"
    if workers >= 1_000_000:
        return f"{workers / 1_000_000:.1f}M"
    if workers >= 1_000:
        return f"{workers / 1_000:.0f}K"
    return str(workers)


def fmt_inr(value: int | None) -> str:
    if value is None:
        return "?"
    return f"INR {value:,}"


def main() -> None:
    with open("occupations.json") as handle:
        occupations = {row["slug"]: row for row in json.load(handle)}
    with open("occupations.csv") as handle:
        csv_rows = {row["slug"]: row for row in csv.DictReader(handle)}
    with open("scores.json") as handle:
        scores = {row["nco2004_3d"]: row for row in json.load(handle)}

    records = []
    for slug, occ in occupations.items():
        row = csv_rows[slug]
        score = scores.get(row["nco2004_3d"], {})
        records.append(
            {
                "title": occ["title"],
                "category": row["category"],
                "nco2004_3d": row["nco2004_3d"],
                "employment_workers": int(row["employment_workers"]),
                "median_monthly_earnings_inr": int(row["median_monthly_earnings_inr"]),
                "vacancies_90d": int(row["vacancies_90d"]),
                "demand_index": int(row["demand_index"]),
                "exposure": score.get("exposure"),
                "exposure_confidence": score.get("exposure_confidence"),
                "rationale": score.get("rationale", ""),
            }
        )

    records.sort(key=lambda row: (-(row["employment_workers"]), -(row["exposure"] or 0)))
    total_workers = sum(row["employment_workers"] for row in records)
    weighted = sum(
        row["employment_workers"] * (row["exposure"] or 0)
        for row in records
        if row["exposure"] is not None
    )
    weighted_exposure = weighted / total_workers if total_workers else 0

    lines = [
        "# AI Exposure of the Indian Job Market",
        "",
        "This document packages the current India adaptation of `karpathy/jobs`.",
        "It uses NCO 2004 3-digit groups as the canonical occupation unit and a blended approximation strategy: seed labour-market estimates, bundled AI exposure scores, and seed demand proxies shaped around the planned PLFS + NCS pipeline.",
        "",
        "## Summary",
        "",
        f"- Occupation groups in bundle: {len(records)}",
        f"- Workers represented in bundle: {total_workers:,}",
        f"- Job-weighted AI exposure: {weighted_exposure:.1f}/10",
        "",
        "## Highest-demand digital and business groups",
        "",
        "| Occupation | NCO 2004 | Workers | Monthly earnings | Demand index | Exposure |",
        "|------------|----------|---------|------------------|--------------|----------|",
    ]

    for row in sorted(records, key=lambda item: (-item["demand_index"], -(item["exposure"] or 0)))[:10]:
        lines.append(
            f"| {row['title']} | {row['nco2004_3d']} | {fmt_workers(row['employment_workers'])} | {fmt_inr(row['median_monthly_earnings_inr'])} | {row['demand_index']} | {row['exposure']}/10 |"
        )

    lines.extend(
        [
            "",
            "## All bundled occupation groups",
            "",
            "| Occupation | Category | Workers | Demand | Exposure | Rationale |",
            "|------------|----------|---------|--------|----------|-----------|",
        ]
    )
    for row in records:
        lines.append(
            f"| {row['title']} | {row['category']} | {fmt_workers(row['employment_workers'])} | {row['demand_index']} | {row['exposure']}/10 | {row['rationale'].replace('|', '/')} |"
        )

    with open("prompt.md", "w") as handle:
        handle.write("\n".join(lines))
    print(f"Wrote prompt.md for {len(records)} occupation groups.")


if __name__ == "__main__":
    main()
