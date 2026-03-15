"""Scrape public NCS job listings, or materialize the bundled seed demand set."""

from __future__ import annotations

import argparse
import json
import os
import time

from playwright.sync_api import sync_playwright

from india_pipeline import RAW_DIR, normalized_seed_records, write_ncs_seed_jobs


SEARCH_URL = "https://www.ncs.gov.in/Pages/Search.aspx"


def scrape_live(max_pages: int, delay: float) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    output_path = os.path.join(RAW_DIR, "ncs_jobs.jsonl")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=30000)

        with open(output_path, "w") as handle:
            for page_number in range(1, max_pages + 1):
                cards = page.locator("div[id*='rptSearchJobs'] h5")
                count = cards.count()
                for index in range(count):
                    card = cards.nth(index)
                    container = card.locator("xpath=ancestor::div[contains(@id,'rptSearchJobs')][1]")
                    title = card.inner_text().strip()
                    snapshot = {
                        "title": title,
                        "source": "live-ncs",
                        "page_number": page_number,
                    }
                    text = container.inner_text()
                    snapshot["raw_text"] = " ".join(text.split())
                    handle.write(json.dumps(snapshot) + "\n")

                next_link = page.locator(f"text='{page_number + 1}'").first
                if page_number >= max_pages or next_link.count() == 0:
                    break
                next_link.click()
                time.sleep(delay)
        browser.close()
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Write the bundled seed demand dataset")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    if args.seed:
        path = write_ncs_seed_jobs(normalized_seed_records())
    else:
        path = scrape_live(args.pages, args.delay)
    print(f"Wrote NCS demand data to {path}")


if __name__ == "__main__":
    main()
