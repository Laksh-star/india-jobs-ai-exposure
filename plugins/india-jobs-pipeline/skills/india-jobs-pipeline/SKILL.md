# India Jobs Pipeline

Use this skill when the user wants to rebuild, validate, or inspect the India jobs AI exposure dataset and static site in this repository.

## Repository detection

Treat the current workspace as compatible only if all of these files exist at the repo root:

- `prepare_india_seed.py`
- `process.py`
- `score.py`
- `build_site_data.py`
- `validate_india_data.py`

If the repo does not match, stop and say the plugin expects the India jobs pipeline layout.

## Default behavior

- Prefer the seed pipeline unless richer raw inputs are clearly present or the user explicitly asks for the production path.
- After any rebuild, always run validation.
- When work completes, summarize generated artifacts with a focus on:
  - `occupations.csv`
  - `scores.json`
  - `site/data.json`
  - `india/processed/occupation_packets.json`

## Seed pipeline

Run:

```bash
python3 plugins/india-jobs-pipeline/scripts/run_seed_pipeline.py
python3 plugins/india-jobs-pipeline/scripts/summarize_outputs.py
```

## Production path

Use the fuller path only when compatible raw files are available or the user explicitly requests it:

```bash
uv run python build_taxonomy.py --from-csv india/raw/nco_3d.csv
uv run python aggregate_plfs.py --input india/raw/plfs_person_level.csv
uv run python scrape.py --pages 10
uv run python process.py
uv run python make_csv.py
uv run python score.py
uv run python build_site_data.py
uv run python validate_india_data.py
python3 plugins/india-jobs-pipeline/scripts/summarize_outputs.py
```

## Validation expectations

- `site/data.json` must contain `canonical_rows`, `display_nodes`, and `meta`.
- Validation must pass through `validate_india_data.py`.
- Surface missing inputs, missing env vars, or score-generation mode clearly.

## Notes

- `score.py` falls back to seed scores when `OPENROUTER_API_KEY` is not set.
- Keep summaries concise and grounded in actual generated files.
