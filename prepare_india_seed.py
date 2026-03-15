"""Materialize the bundled India demo dataset into the repo outputs."""

from india_pipeline import normalized_seed_records, write_seed_snapshot


def main() -> None:
    records = normalized_seed_records()
    write_seed_snapshot(records)
    print(f"Wrote seed India dataset for {len(records)} occupation groups.")


if __name__ == "__main__":
    main()
