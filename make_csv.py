"""Build the India occupations.csv summary file."""

from india_pipeline import load_packets, write_occupations_csv


def main() -> None:
    records = load_packets()
    write_occupations_csv(records)
    total_workers = sum(record["employment_workers"] for record in records)
    print(f"Wrote {len(records)} rows to occupations.csv")
    print(f"Total workers represented: {total_workers:,}")


if __name__ == "__main__":
    main()
