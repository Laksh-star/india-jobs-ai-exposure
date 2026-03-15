# `india/raw/` input contract

This directory is intentionally mostly empty in git.

The repository ships only redistributable seed/demo inputs, such as `ncs_jobs.jsonl`, so that the India demo build stays runnable without licensed or gated datasets.

## What is expected here for a fuller build

### `plfs_person_level.csv`

Input for `aggregate_plfs.py`.

Expected columns:

- `nco_2004_code`
- `person_weight`
- `monthly_earnings_inr`
- `education_bucket`
- `rural_urban`

Notes:

- This is an exported or transformed CSV derived from PLFS person-level data.
- The repository does not redistribute PLFS microdata.
- If access to person-level PLFS is not available, you can adapt the pipeline to published aggregates, but that is outside the current demo path.

### `nco_3d.csv`

Input for `build_taxonomy.py --from-csv india/raw/nco_3d.csv`.

Expected columns:

- `nco2004_3d`
- `title`
- `nco2015_3d`
- `category`

Use this file to define the canonical India occupation universe and the NCO 2004 to NCO 2015 crosswalk used by the rest of the repo.

### Optional NCS scrape artifacts

You may also place scrape outputs here if you want to keep raw captures out of the repo root, for example:

- `ncs_jobs.jsonl`
- NCS occupation-detail exports
- crosswalk helper files

## Seed/demo vs production inputs

- Seed/demo: redistributed in git when needed to keep the example build runnable.
- Production inputs: documented here, but intentionally not committed if they come from gated, bulky, or non-redistributable sources.

## Source-acquisition notes

- PLFS data is not bundled here. Obtain it through your permitted MoSPI / microdata access path or use approved transformed extracts.
- NCO title tables and crosswalks should be assembled from official labour-classification references before use in production.
- Public NCS listings can be scraped with `scrape.py`, but raw snapshots may contain noisy or duplicate postings and should be treated as ephemeral inputs.
