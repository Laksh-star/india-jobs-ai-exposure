"""Validate the India site payload and generated source files."""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

from india_pipeline import OCCUPATIONS_CSV, OCCUPATIONS_JSON, PROCESSED_DIR, SCORES_JSON


REQUIRED_CANONICAL_FIELDS = {
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

REQUIRED_NODE_FIELDS = {
    "node_id",
    "node_kind",
    "parent_id",
    "title",
    "employment_workers",
    "worker_share",
    "median_monthly_earnings_inr",
    "demand_index",
    "vacancies_90d",
    "exposure",
    "exposure_confidence",
    "approximation_level",
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
        os.path.join("india", "display_roles.json"),
    ):
        if not os.path.exists(path):
            fail(f"Missing required file: {path}")

    with open(os.path.join("site", "data.json")) as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        fail("site/data.json must be an object payload")

    for key in ("canonical_rows", "display_nodes", "meta"):
        if key not in payload:
            fail(f"Missing top-level site payload key: {key}")

    canonical_rows = payload["canonical_rows"]
    display_nodes = payload["display_nodes"]
    meta = payload["meta"]
    if not canonical_rows:
        fail("site/data.json canonical_rows is empty")
    if not display_nodes:
        fail("site/data.json display_nodes is empty")

    for record in canonical_rows:
        missing = REQUIRED_CANONICAL_FIELDS - set(record)
        if missing:
            fail(f"Missing fields in canonical record {record.get('title')}: {sorted(missing)}")
        if record["country"] != "India":
            fail(f"Unexpected country in canonical record: {record['country']}")
        if not isinstance(record["sources"], list) or not record["sources"]:
            fail(f"Canonical record {record['title']} has no sources")
        if record["employment_workers"] <= 0:
            fail(f"Canonical record {record['title']} has non-positive employment")

    node_map = {}
    children = defaultdict(list)
    for node in display_nodes:
        missing = REQUIRED_NODE_FIELDS - set(node)
        if missing:
            fail(f"Missing fields in display node {node.get('title')}: {sorted(missing)}")
        if node["node_id"] in node_map:
            fail(f"Duplicate display node id: {node['node_id']}")
        node_map[node["node_id"]] = node
        children[node["parent_id"]].append(node)
        if node["employment_workers"] <= 0:
            fail(f"Display node {node['title']} has non-positive employment")
        if not isinstance(node["sources"], list) or not node["sources"]:
            fail(f"Display node {node['title']} has no sources")

    for node in display_nodes:
        if node["parent_id"] is not None and node["parent_id"] not in node_map:
            fail(f"Display node {node['node_id']} has invalid parent {node['parent_id']}")

    major_nodes = [node for node in display_nodes if node["node_kind"] == "major_group"]
    nco_nodes = [node for node in display_nodes if node["node_kind"] == "nco_group"]
    role_nodes = [node for node in display_nodes if node["node_kind"] == "role"]

    if len(role_nodes) < 90 or len(role_nodes) > 110:
        fail(f"Expected 90-110 display leaves, found {len(role_nodes)}")

    canonical_by_nco = {row["nco2004_3d"]: row for row in canonical_rows}
    for node in nco_nodes:
        code = node["canonical_nco2004_3d"]
        canonical = canonical_by_nco.get(code)
        if not canonical:
            fail(f"NCO display node {node['node_id']} has no canonical row")
        if node["employment_workers"] != canonical["employment_workers"]:
            fail(f"NCO node {node['node_id']} employment does not match canonical row")

    for node in role_nodes:
        parent = node_map.get(node["parent_id"])
        if not parent or parent["node_kind"] != "nco_group":
            fail(f"Role node {node['node_id']} has invalid parent chain")
        if node["exposure_confidence"] >= parent["exposure_confidence"]:
            fail(f"Role node {node['node_id']} must have lower confidence than parent")
        if node["approximation_level"] != "derived-role":
            fail(f"Role node {node['node_id']} must be marked derived-role")

    for parent in nco_nodes:
        child_sum = sum(node["employment_workers"] for node in children[parent["node_id"]])
        if child_sum != parent["employment_workers"]:
            fail(f"Role employment does not reconcile for {parent['node_id']}")

    for parent in major_nodes:
        child_sum = sum(node["employment_workers"] for node in children[parent["node_id"]])
        if child_sum != parent["employment_workers"]:
            fail(f"NCO employment does not reconcile for {parent['node_id']}")

    if meta.get("canonical_row_count") != len(canonical_rows):
        fail("meta.canonical_row_count does not match canonical_rows length")
    if meta.get("display_node_count") != len(display_nodes):
        fail("meta.display_node_count does not match display_nodes length")
    if meta.get("display_leaf_count") != len(role_nodes):
        fail("meta.display_leaf_count does not match role node count")

    print(
        f"Validated {len(canonical_rows)} canonical rows, "
        f"{len(display_nodes)} display nodes, and {len(role_nodes)} display leaves."
    )


if __name__ == "__main__":
    main()
