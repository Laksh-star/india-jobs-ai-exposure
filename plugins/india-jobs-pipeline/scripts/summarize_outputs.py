#!/usr/bin/env python3
"""Summarize the main generated outputs for the India jobs repo."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def load_json(path: Path):
    with path.open() as handle:
        return json.load(handle)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    occupations_csv = repo_root / "occupations.csv"
    scores_json = repo_root / "scores.json"
    site_data_json = repo_root / "site" / "data.json"
    packets_json = repo_root / "india" / "processed" / "occupation_packets.json"

    required = [occupations_csv, scores_json, site_data_json, packets_json]
    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    if missing:
        print("Missing generated outputs:")
        for path in missing:
            print(f"- {path}")
        return 1

    with occupations_csv.open(newline="") as handle:
        occupations = list(csv.DictReader(handle))

    scores = load_json(scores_json)
    site_data = load_json(site_data_json)
    packets = load_json(packets_json)

    canonical_rows = site_data.get("canonical_rows", [])
    display_nodes = site_data.get("display_nodes", [])
    meta = site_data.get("meta", {})
    display_roles = [node for node in display_nodes if node.get("node_kind") == "role"]

    exposures = [
        row.get("exposure")
        for row in canonical_rows
        if isinstance(row.get("exposure"), (int, float))
    ]
    avg_exposure = round(sum(exposures) / len(exposures), 2) if exposures else None

    print("India jobs output summary")
    print(f"- occupations.csv rows: {len(occupations)}")
    print(f"- scores.json rows: {len(scores)}")
    print(f"- occupation packets: {len(packets)}")
    print(f"- canonical rows: {len(canonical_rows)}")
    print(f"- display nodes: {len(display_nodes)}")
    print(f"- display leaves: {len(display_roles)}")
    print(f"- meta canonical_row_count: {meta.get('canonical_row_count')}")
    print(f"- meta display_node_count: {meta.get('display_node_count')}")
    print(f"- meta display_leaf_count: {meta.get('display_leaf_count')}")
    if avg_exposure is not None:
        print(f"- average canonical exposure: {avg_exposure}")

    top_rows = sorted(
        canonical_rows,
        key=lambda row: row.get("employment_workers", 0),
        reverse=True,
    )[:3]
    if top_rows:
        print("- top canonical groups by employment:")
        for row in top_rows:
            print(
                f"  - {row.get('nco2004_3d')} {row.get('title')}: "
                f"{row.get('employment_workers')} workers, exposure {row.get('exposure')}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
