"""Score India occupation packets for AI exposure, or materialize seed scores."""

from __future__ import annotations

import argparse
import json
import os
import time

from india_pipeline import load_packets, seed_scores, write_scores_json

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on environment
    def load_dotenv() -> None:
        return None

load_dotenv()

DEFAULT_MODEL = "google/gemini-3-flash-preview"
OUTPUT_FILE = "scores.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """\
You are an expert analyst evaluating how exposed Indian occupation groups are to AI.
You will be given a markdown packet describing one NCO 2004 3-digit occupation group.

Rate the occupation group's overall **AI Exposure** on a scale from 0 to 10.

AI Exposure measures how much AI will reshape the occupation group in India.
Consider:
- direct automation of current tasks
- indirect headcount compression from higher worker productivity
- uneven digitization across India
- low labor-cost substitution barriers
- informality and fragmented enterprises
- physical-world constraints, regulation, safety, and trust

Use this broad calibration:
- 0-1: almost entirely physical/manual and locally executed
- 2-3: low exposure, AI mostly affects admin edges
- 4-5: mixed work, meaningful assistance but physical or in-person core remains
- 6-7: high exposure, major digital coordination/knowledge component
- 8-9: very high exposure, mostly computer-based and documentation-heavy
- 10: routine digital information processing with minimal physical component

Respond with ONLY valid JSON in this exact structure:
{
  "exposure": <0-10 integer>,
  "exposure_confidence": <0-1 number>,
  "rationale": "<2-3 sentences>",
  "evidence_sources": ["<short item>", "<short item>"]
}\
"""


def score_occupation(client, text: str, model: str) -> dict:
    response = client.post(
        API_URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    return json.loads(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--seed", action="store_true", help="Write bundled seed scores instead of calling an API")
    args = parser.parse_args()

    records = load_packets()[args.start:args.end]
    if args.seed or "OPENROUTER_API_KEY" not in os.environ:
        write_scores_json(records)
        print(f"Wrote seed scores for {len(records)} occupation groups.")
        return

    scores = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as handle:
            for row in json.load(handle):
                scores[row["nco2004_3d"]] = row

    import httpx

    client = httpx.Client()
    errors = []
    for index, record in enumerate(records, start=1):
        code = record["nco2004_3d"]
        if code in scores:
            continue

        md_path = os.path.join("pages", f"{record['slug']}.md")
        if not os.path.exists(md_path):
            print(f"[{index}] SKIP {code} (missing markdown)")
            continue
        with open(md_path) as handle:
            text = handle.read()

        print(f"[{index}/{len(records)}] {record['title']}...", end=" ", flush=True)
        try:
            result = score_occupation(client, text, args.model)
            scores[code] = {"nco2004_3d": code, "title": record["title"], **result}
            print(f"exposure={result['exposure']}")
        except Exception as exc:  # pragma: no cover - exercised manually
            print(f"ERROR: {exc}")
            errors.append(code)

        with open(OUTPUT_FILE, "w") as handle:
            json.dump(list(scores.values()), handle, indent=2)

        if index < len(records):
            time.sleep(args.delay)

    client.close()
    print(f"Done. Scored {len(scores)} occupation groups, {len(errors)} errors.")


if __name__ == "__main__":
    main()
