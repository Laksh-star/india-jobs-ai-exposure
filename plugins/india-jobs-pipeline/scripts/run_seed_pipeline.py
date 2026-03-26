#!/usr/bin/env python3
"""Run the documented seed pipeline for the India jobs repo."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from shutil import which


REQUIRED_FILES = [
    "prepare_india_seed.py",
    "process.py",
    "make_csv.py",
    "score.py",
    "build_site_data.py",
    "make_prompt.py",
    "validate_india_data.py",
]


def build_commands() -> list[list[str]]:
    python = sys.executable
    if which("uv"):
        runner = ["uv", "run", "python"]
    else:
        runner = [python]

    return [
        [*runner, "prepare_india_seed.py"],
        [*runner, "process.py", "--seed"],
        [*runner, "make_csv.py"],
        [*runner, "score.py", "--seed"],
        [*runner, "build_site_data.py"],
        [*runner, "make_prompt.py"],
        [*runner, "validate_india_data.py"],
    ]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    missing = [name for name in REQUIRED_FILES if not (repo_root / name).exists()]
    if missing:
        print("Repository layout does not match the India jobs pipeline.")
        for name in missing:
            print(f"- missing: {name}")
        return 1

    print(f"Running seed pipeline in {repo_root}")
    for command in build_commands():
        print(f"\n$ {' '.join(command)}")
        result = subprocess.run(command, cwd=repo_root)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            return result.returncode

    print("\nSeed pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
