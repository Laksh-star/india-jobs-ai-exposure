# AI Exposure of the Indian Job Market

Adapted from [`karpathy/jobs`](https://github.com/karpathy/jobs), with the same static-site shape and a rewritten India-specific labour-market pipeline based on **NCO 2004 3-digit occupation groups**.

This repository is an adaptation, not a forked continuation of the upstream project. Upstream remains Karpathy's original US-market implementation.

The repo now ships with a transparent **seed dataset** so the site is runnable without PLFS microdata or live NCS scraping. The production path is still the same 5-stage idea: build taxonomy, ingest labour stats, ingest demand, generate packets, score AI exposure, and ship a static treemap.

## What's here

- `prepare_india_seed.py` materializes the bundled India demo dataset.
- `build_taxonomy.py` builds the canonical `nco2004_3d` taxonomy.
- `aggregate_plfs.py` aggregates PLFS-style person-level CSV into `india/processed/plfs_aggregates.json`.
- `scrape.py` scrapes public NCS job listings or writes a seed demand snapshot.
- `process.py` writes occupation packets and Markdown pages.
- `make_csv.py` builds `occupations.csv` in the India schema.
- `score.py` scores occupation groups with an LLM or writes the bundled seed scores.
- `build_site_data.py` produces `site/data.json`.
- `validate_india_data.py` validates the generated site payload.

## Data model

The canonical join key is **`nco2004_3d`**. The site payload includes:

- `country`
- `nco2004_3d`
- `nco2015_3d`
- `employment_workers`
- `worker_share`
- `median_monthly_earnings_inr`
- `demand_index`
- `vacancies_90d`
- `exposure`
- `exposure_confidence`
- `education_mix`
- `rural_urban_split`
- `sources`

## Seed demo

This is the fast path for a working local build:

```bash
uv run python prepare_india_seed.py
uv run python process.py --seed
uv run python make_csv.py
uv run python score.py --seed
uv run python build_site_data.py
uv run python make_prompt.py
uv run python validate_india_data.py
cd site && python -m http.server 8000
```

The seed bundle is intentionally explicit about its status:

- Occupation groups are real NCO-style groups.
- Labour counts, pay, and demand are seed approximations.
- `sources` and confidence fields stay visible in the site payload.

## Production pipeline

Use these source baselines for a fuller build:

- PLFS 2023-24 person-level microdata or an exported CSV with `nco_2004_code`, `person_weight`, `monthly_earnings_inr`, `education_bucket`, and `rural_urban`
- NCO 2004 / NCO 2015 crosswalk and title tables
- Public NCS job-search listings
- NCS career information / occupation-detail text

Suggested flow:

```bash
uv run python build_taxonomy.py --from-csv india/raw/nco_3d.csv
uv run python aggregate_plfs.py --input india/raw/plfs_person_level.csv
uv run python scrape.py --pages 10
uv run python process.py
uv run python make_csv.py
uv run python score.py
uv run python build_site_data.py
uv run python validate_india_data.py
```

`process.py` and `make_csv.py` currently default to the seed bundle when richer upstream files are not present. That keeps the repo runnable while leaving room for the real PLFS + NCS ingestion path.

## Setup

```bash
uv sync
uv run playwright install chromium
```

OpenRouter scoring still requires:

```bash
OPENROUTER_API_KEY=your_key_here
```
