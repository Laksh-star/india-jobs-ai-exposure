"""Helpers for the India adaptation pipeline."""

from __future__ import annotations

import csv
import json
import os
import re
from typing import Any

from india_seed import SEED_RECORDS


ROOT = os.path.dirname(os.path.abspath(__file__))
INDIA_DIR = os.path.join(ROOT, "india")
RAW_DIR = os.path.join(INDIA_DIR, "raw")
PROCESSED_DIR = os.path.join(INDIA_DIR, "processed")
PAGES_DIR = os.path.join(ROOT, "pages")
SITE_DIR = os.path.join(ROOT, "site")
OCCUPATIONS_JSON = os.path.join(ROOT, "occupations.json")
OCCUPATIONS_CSV = os.path.join(ROOT, "occupations.csv")
SCORES_JSON = os.path.join(ROOT, "scores.json")


EDUCATION_PROFILES = {
    "agri": {
        "Below secondary": 62,
        "Secondary": 26,
        "Diploma/Certificate": 5,
        "Graduate": 6,
        "Postgraduate+": 1,
    },
    "service": {
        "Below secondary": 36,
        "Secondary": 36,
        "Diploma/Certificate": 11,
        "Graduate": 14,
        "Postgraduate+": 3,
    },
    "trades": {
        "Below secondary": 33,
        "Secondary": 40,
        "Diploma/Certificate": 17,
        "Graduate": 8,
        "Postgraduate+": 2,
    },
    "mixed-clerical": {
        "Below secondary": 12,
        "Secondary": 34,
        "Diploma/Certificate": 16,
        "Graduate": 30,
        "Postgraduate+": 8,
    },
    "graduate-heavy": {
        "Below secondary": 2,
        "Secondary": 10,
        "Diploma/Certificate": 12,
        "Graduate": 54,
        "Postgraduate+": 22,
    },
    "health": {
        "Below secondary": 1,
        "Secondary": 14,
        "Diploma/Certificate": 28,
        "Graduate": 42,
        "Postgraduate+": 15,
    },
    "teaching": {
        "Below secondary": 4,
        "Secondary": 18,
        "Diploma/Certificate": 10,
        "Graduate": 48,
        "Postgraduate+": 20,
    },
}

RURAL_URBAN_PROFILES = {
    "rural": {"rural": 84, "urban": 16},
    "mixed": {"rural": 56, "urban": 44},
    "peri-urban": {"rural": 42, "urban": 58},
    "urban": {"rural": 18, "urban": 82},
}

DEFAULT_SOURCES = [
    {
        "name": "NCO 2004 group title",
        "type": "official-taxonomy",
        "status": "seeded",
    },
    {
        "name": "PLFS 2023-24 aggregate placeholder",
        "type": "official-labour-stats",
        "status": "approximation",
    },
    {
        "name": "NCS vacancy proxy placeholder",
        "type": "demand-proxy",
        "status": "approximation",
    },
]


def ensure_dirs() -> None:
    for path in (INDIA_DIR, RAW_DIR, PROCESSED_DIR, PAGES_DIR, SITE_DIR):
        os.makedirs(path, exist_ok=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def total_seed_workers(records: list[dict[str, Any]] | None = None) -> int:
    source = records if records is not None else SEED_RECORDS
    return sum(int(record["employment_workers"]) for record in source)


def normalized_seed_records() -> list[dict[str, Any]]:
    total_workers = total_seed_workers()
    records = []
    for seed in SEED_RECORDS:
        education_mix = EDUCATION_PROFILES[seed["education_profile"]]
        rural_urban_split = RURAL_URBAN_PROFILES[seed["rural_urban_profile"]]
        employment = int(seed["employment_workers"])
        monthly = int(seed["median_monthly_earnings_inr"])
        record = {
            "country": "India",
            "title": seed["title"],
            "slug": f"{seed['nco2004_3d']}-{slugify(seed['title'])}",
            "category": seed["category"],
            "nco2004_3d": seed["nco2004_3d"],
            "nco2015_3d": seed["nco2015_3d"],
            "employment_workers": employment,
            "worker_share": round((employment / total_workers) * 100, 2),
            "median_monthly_earnings_inr": monthly,
            "median_annual_earnings_inr": monthly * 12,
            "vacancies_90d": int(seed["vacancies_90d"]),
            "demand_index": int(seed["demand_index"]),
            "exposure": int(seed["exposure"]),
            "exposure_confidence": float(seed["exposure_confidence"]),
            "education_mix": education_mix,
            "rural_urban_split": rural_urban_split,
            "summary": seed["summary"],
            "task_line": seed["task_line"],
            "ai_notes": seed["ai_notes"],
            "sample_postings": list(seed["sample_postings"]),
            "rationale": seed["rationale"],
            "sources": list(DEFAULT_SOURCES),
            "description_source": "seed-demo",
            "postings_source": "seed-demo",
            "plfs_pay_confidence": "approximation",
            "employment_confidence": "approximation",
            "demand_confidence": "approximation",
            "url": "https://www.ncs.gov.in/Pages/Search.aspx",
        }
        records.append(record)
    return records


def markdown_for_record(record: dict[str, Any]) -> str:
    sources = "\n".join(
        f"- {source['name']} ({source['type']}, {source['status']})"
        for source in record["sources"]
    )
    postings = "\n".join(f"- {posting}" for posting in record["sample_postings"])
    education = "\n".join(
        f"- **{label}:** {value}%"
        for label, value in record["education_mix"].items()
    )
    split = "\n".join(
        f"- **{label.title()}:** {value}%"
        for label, value in record["rural_urban_split"].items()
    )
    return "\n".join(
        [
            f"# {record['title']}",
            "",
            f"**Country:** {record['country']}",
            f"**NCO 2004 group:** {record['nco2004_3d']}",
            f"**NCO 2015 group:** {record['nco2015_3d']}",
            f"**Category:** {record['category']}",
            "",
            "## Labour-market estimate",
            "",
            f"- **Employment workers:** {record['employment_workers']:,}",
            f"- **Worker share:** {record['worker_share']:.2f}%",
            f"- **Median monthly earnings:** INR {record['median_monthly_earnings_inr']:,}",
            f"- **Vacancies last 90d:** {record['vacancies_90d']:,}",
            f"- **Demand index:** {record['demand_index']}/100",
            "",
            "## Occupation summary",
            "",
            record["summary"],
            "",
            record["task_line"],
            "",
            "## AI exposure notes",
            "",
            record["ai_notes"],
            "",
            "## Education mix",
            "",
            education,
            "",
            "## Rural/urban split",
            "",
            split,
            "",
            "## Representative public-job wording",
            "",
            postings,
            "",
            "## Data provenance",
            "",
            sources,
            "",
        ]
    )


def write_pages(records: list[dict[str, Any]]) -> None:
    ensure_dirs()
    for record in records:
        path = os.path.join(PAGES_DIR, f"{record['slug']}.md")
        with open(path, "w") as handle:
            handle.write(markdown_for_record(record))


def write_occupations_json(records: list[dict[str, Any]]) -> None:
    payload = [
        {
            "title": record["title"],
            "slug": record["slug"],
            "category": record["category"],
            "country": record["country"],
            "nco2004_3d": record["nco2004_3d"],
            "nco2015_3d": record["nco2015_3d"],
            "url": record["url"],
        }
        for record in records
    ]
    with open(OCCUPATIONS_JSON, "w") as handle:
        json.dump(payload, handle, indent=2)


def write_packets_json(records: list[dict[str, Any]]) -> None:
    ensure_dirs()
    with open(os.path.join(PROCESSED_DIR, "occupation_packets.json"), "w") as handle:
        json.dump(records, handle, indent=2)


def write_occupations_csv(records: list[dict[str, Any]]) -> None:
    fieldnames = [
        "title",
        "slug",
        "country",
        "category",
        "nco2004_3d",
        "nco2015_3d",
        "employment_workers",
        "worker_share",
        "median_monthly_earnings_inr",
        "median_annual_earnings_inr",
        "plfs_pay_confidence",
        "employment_confidence",
        "vacancies_90d",
        "demand_index",
        "demand_confidence",
        "education_mix_json",
        "rural_urban_split_json",
        "sources_json",
        "description_source",
        "postings_source",
        "url",
    ]
    with open(OCCUPATIONS_CSV, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "title": record["title"],
                    "slug": record["slug"],
                    "country": record["country"],
                    "category": record["category"],
                    "nco2004_3d": record["nco2004_3d"],
                    "nco2015_3d": record["nco2015_3d"],
                    "employment_workers": record["employment_workers"],
                    "worker_share": f"{record['worker_share']:.2f}",
                    "median_monthly_earnings_inr": record["median_monthly_earnings_inr"],
                    "median_annual_earnings_inr": record["median_annual_earnings_inr"],
                    "plfs_pay_confidence": record["plfs_pay_confidence"],
                    "employment_confidence": record["employment_confidence"],
                    "vacancies_90d": record["vacancies_90d"],
                    "demand_index": record["demand_index"],
                    "demand_confidence": record["demand_confidence"],
                    "education_mix_json": json.dumps(record["education_mix"], sort_keys=True),
                    "rural_urban_split_json": json.dumps(
                        record["rural_urban_split"], sort_keys=True
                    ),
                    "sources_json": json.dumps(record["sources"]),
                    "description_source": record["description_source"],
                    "postings_source": record["postings_source"],
                    "url": record["url"],
                }
            )


def seed_scores(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "nco2004_3d": record["nco2004_3d"],
            "title": record["title"],
            "exposure": record["exposure"],
            "exposure_confidence": record["exposure_confidence"],
            "rationale": record["rationale"],
            "evidence_sources": [
                "Occupation markdown packet",
                "Bundled India seed dataset",
            ],
        }
        for record in records
    ]


def write_scores_json(records: list[dict[str, Any]]) -> None:
    with open(SCORES_JSON, "w") as handle:
        json.dump(seed_scores(records), handle, indent=2)


def load_packets() -> list[dict[str, Any]]:
    packets_path = os.path.join(PROCESSED_DIR, "occupation_packets.json")
    if os.path.exists(packets_path):
        with open(packets_path) as handle:
            return json.load(handle)
    return normalized_seed_records()


def write_ncs_seed_jobs(records: list[dict[str, Any]]) -> str:
    ensure_dirs()
    path = os.path.join(RAW_DIR, "ncs_jobs.jsonl")
    with open(path, "w") as handle:
        for record in records:
            for posting in record["sample_postings"]:
                handle.write(
                    json.dumps(
                        {
                            "title": posting,
                            "occupation_title": record["title"],
                            "nco2004_3d": record["nco2004_3d"],
                            "category": record["category"],
                            "salary_type": "monthly",
                            "salary_min": record["median_monthly_earnings_inr"],
                            "salary_max": int(record["median_monthly_earnings_inr"] * 1.25),
                            "source": "seed-demo",
                            "portal": "NCS",
                        }
                    )
                    + "\n"
                )
    return path


def write_seed_snapshot(records: list[dict[str, Any]]) -> None:
    ensure_dirs()
    write_packets_json(records)
    write_pages(records)
    write_occupations_json(records)
    write_occupations_csv(records)
    write_scores_json(records)
    write_ncs_seed_jobs(records)

