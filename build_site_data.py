"""Build the static site payload for the India labour-market view."""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict

from india_pipeline import PROCESSED_DIR


DISPLAY_ROLES_PATH = os.path.join("india", "display_roles.json")
PACKETS_PATH = os.path.join(PROCESSED_DIR, "occupation_packets.json")

MAJOR_GROUP_LABELS = {
    "1": "Managers and senior officials",
    "2": "Professionals",
    "3": "Technicians and associate professionals",
    "4": "Clerks",
    "5": "Service, sales and care workers",
    "6": "Skilled agricultural and fishery workers",
    "7": "Craft and related trades workers",
    "8": "Plant, machine operators and assemblers",
    "9": "Elementary occupations",
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def weighted_average(rows: list[dict], key: str) -> float:
    total_workers = sum(row["employment_workers"] for row in rows)
    if not total_workers:
        return 0.0
    return sum(row[key] * row["employment_workers"] for row in rows) / total_workers


def dedupe_sources(rows: list[dict]) -> list[dict]:
    seen = set()
    merged = []
    for row in rows:
        for source in row["sources"]:
            key = (source.get("name"), source.get("type"), source.get("status"))
            if key in seen:
                continue
            seen.add(key)
            merged.append(source)
    return merged


def allocate_integer_total(total: int, weights: list[float]) -> list[int]:
    if total <= 0 or not weights or sum(weights) <= 0:
        return [0 for _ in weights]
    weight_sum = sum(weights)
    raw = [(total * weight) / weight_sum for weight in weights]
    base = [int(value) for value in raw]
    remainder = total - sum(base)
    fractions = sorted(
        range(len(raw)),
        key=lambda idx: (raw[idx] - base[idx]),
        reverse=True,
    )
    for idx in fractions[:remainder]:
        base[idx] += 1
    return base


def load_packets() -> dict[str, dict]:
    with open(PACKETS_PATH) as handle:
        return {row["nco2004_3d"]: row for row in json.load(handle)}


def load_display_roles() -> dict[str, list[dict]]:
    with open(DISPLAY_ROLES_PATH) as handle:
        payload = json.load(handle)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for role in payload:
        grouped[role["parent_nco2004_3d"]].append(role)
    return grouped


def build_canonical_rows() -> list[dict]:
    with open("scores.json") as handle:
        scores = {row["nco2004_3d"]: row for row in json.load(handle)}
    packets = load_packets()

    rows = []
    with open("occupations.csv") as handle:
        for row in csv.DictReader(handle):
            score = scores.get(row["nco2004_3d"], {})
            packet = packets.get(row["nco2004_3d"], {})
            rows.append(
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
                    "summary": packet.get("summary", ""),
                    "task_line": packet.get("task_line", ""),
                    "ai_notes": packet.get("ai_notes", ""),
                    "sample_postings": packet.get("sample_postings", []),
                    "url": row["url"],
                }
            )
    return rows


def build_major_group_nodes(canonical_rows: list[dict], total_workers: int) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in canonical_rows:
        grouped[row["nco2004_3d"][0]].append(row)

    nodes = []
    for key, rows in grouped.items():
        employment = sum(row["employment_workers"] for row in rows)
        nodes.append(
            {
                "node_id": f"major-{key}",
                "node_kind": "major_group",
                "parent_id": None,
                "title": MAJOR_GROUP_LABELS.get(key, "Other / Unmapped"),
                "canonical_nco2004_3d": None,
                "category": None,
                "employment_workers": employment,
                "worker_share": round((employment / total_workers) * 100, 2),
                "median_monthly_earnings_inr": int(round(weighted_average(rows, "median_monthly_earnings_inr"))),
                "demand_index": int(round(weighted_average(rows, "demand_index"))),
                "vacancies_90d": sum(row["vacancies_90d"] for row in rows),
                "exposure": round(weighted_average(rows, "exposure"), 1),
                "exposure_confidence": round(weighted_average(rows, "exposure_confidence"), 2),
                "approximation_level": "aggregated-major-group",
                "sources": [
                    {
                        "name": "Aggregated from canonical NCO groups",
                        "type": "display-aggregation",
                        "status": "derived",
                    }
                ],
                "summary": f"Aggregates {len(rows)} canonical NCO 2004 groups into this major group.",
                "display_child_count": len(rows),
            }
        )
    return sorted(nodes, key=lambda row: row["employment_workers"], reverse=True)


def build_nco_group_nodes(canonical_rows: list[dict], role_defs: dict[str, list[dict]]) -> list[dict]:
    nodes = []
    for row in canonical_rows:
        share_total = sum(role["share"] for role in role_defs.get(row["nco2004_3d"], []))
        residual_count = 1 if share_total < 0.999 else 0
        nodes.append(
            {
                "node_id": f"nco-{row['nco2004_3d']}",
                "node_kind": "nco_group",
                "parent_id": f"major-{row['nco2004_3d'][0]}",
                "title": row["title"],
                "canonical_nco2004_3d": row["nco2004_3d"],
                "category": row["category"],
                "employment_workers": row["employment_workers"],
                "worker_share": row["worker_share"],
                "median_monthly_earnings_inr": row["median_monthly_earnings_inr"],
                "demand_index": row["demand_index"],
                "vacancies_90d": row["vacancies_90d"],
                "exposure": float(row["exposure"]),
                "exposure_confidence": float(row["exposure_confidence"]),
                "approximation_level": "canonical-group",
                "sources": row["sources"],
                "summary": row["summary"] or row["task_line"],
                "display_child_count": len(role_defs.get(row["nco2004_3d"], [])) + residual_count,
            }
        )
    return sorted(nodes, key=lambda row: row["employment_workers"], reverse=True)


def build_role_nodes(canonical_rows: list[dict], role_defs: dict[str, list[dict]], total_workers: int) -> list[dict]:
    nodes = []
    for row in canonical_rows:
        canonical_code = row["nco2004_3d"]
        roles = list(role_defs.get(canonical_code, []))
        share_total = round(sum(role["share"] for role in roles), 4)
        if share_total > 1.0:
            raise ValueError(f"Display role shares exceed 1.0 for {canonical_code}")
        residual_share = round(1.0 - share_total, 4)
        if residual_share > 0.0001:
            roles.append(
                {
                    "role_id": f"role-{canonical_code}-other-general",
                    "parent_nco2004_3d": canonical_code,
                    "title": "Other / General",
                    "share": residual_share,
                    "source_basis": "curated",
                    "pay_multiplier": 0.95,
                    "demand_multiplier": 0.95,
                    "exposure_offset": -0.2,
                    "role_summary": "Residual share for general work inside the canonical occupation group.",
                }
            )

        employment = allocate_integer_total(
            row["employment_workers"],
            [role["share"] for role in roles],
        )
        vacancies = allocate_integer_total(
            row["vacancies_90d"],
            [role["share"] * role["demand_multiplier"] for role in roles],
        )

        for role, role_employment, role_vacancies in zip(roles, employment, vacancies):
            nodes.append(
                {
                    "node_id": role["role_id"],
                    "node_kind": "role",
                    "parent_id": f"nco-{canonical_code}",
                    "title": role["title"],
                    "canonical_nco2004_3d": canonical_code,
                    "category": row["category"],
                    "employment_workers": role_employment,
                    "worker_share": round((role_employment / total_workers) * 100, 2),
                    "median_monthly_earnings_inr": int(round(row["median_monthly_earnings_inr"] * role["pay_multiplier"])),
                    "demand_index": int(round(clamp(row["demand_index"] * role["demand_multiplier"], 0, 100))),
                    "vacancies_90d": role_vacancies,
                    "exposure": round(clamp(row["exposure"] + role["exposure_offset"], 0, 10), 1),
                    "exposure_confidence": round(max(0.35, row["exposure_confidence"] - 0.08), 2),
                    "approximation_level": "derived-role",
                    "sources": [
                        {
                            "name": "Curated display role taxonomy",
                            "type": "display-taxonomy",
                            "status": role["source_basis"],
                        },
                        {
                            "name": "Derived from parent NCO 2004 group",
                            "type": "derived-from-parent",
                            "status": "approximation",
                        },
                    ],
                    "summary": role["role_summary"],
                    "role_share": role["share"],
                    "source_basis": role["source_basis"],
                }
            )
    return nodes


def build_payload() -> dict:
    canonical_rows = build_canonical_rows()
    total_workers = sum(row["employment_workers"] for row in canonical_rows)
    role_defs = load_display_roles()

    major_nodes = build_major_group_nodes(canonical_rows, total_workers)
    nco_group_nodes = build_nco_group_nodes(canonical_rows, role_defs)
    role_nodes = build_role_nodes(canonical_rows, role_defs, total_workers)

    payload = {
        "canonical_rows": canonical_rows,
        "display_nodes": major_nodes + nco_group_nodes + role_nodes,
        "meta": {
            "country": "India",
            "payload_version": 2,
            "canonical_row_count": len(canonical_rows),
            "display_node_count": len(major_nodes) + len(nco_group_nodes) + len(role_nodes),
            "display_leaf_count": len(role_nodes),
            "root_node_count": len(major_nodes),
            "approximation_note": "Representative role nodes are display-layer approximations derived from canonical NCO 2004 groups.",
        },
    }
    return payload


def main() -> None:
    payload = build_payload()

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as handle:
        json.dump(payload, handle)

    total_workers = sum(record["employment_workers"] for record in payload["canonical_rows"])
    print(
        "Wrote "
        f"{payload['meta']['canonical_row_count']} canonical rows and "
        f"{payload['meta']['display_leaf_count']} display leaves to site/data.json"
    )
    print(f"Total workers represented: {total_workers:,}")


if __name__ == "__main__":
    main()
