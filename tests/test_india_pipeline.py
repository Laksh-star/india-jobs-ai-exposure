import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class IndiaPipelineTests(unittest.TestCase):
    def run_cmd(self, *args):
        subprocess.run([sys.executable, *args], cwd=ROOT, check=True)

    def test_seed_pipeline_materializes_outputs(self):
        self.run_cmd("prepare_india_seed.py")
        self.run_cmd("process.py", "--seed")
        self.run_cmd("make_csv.py")
        self.run_cmd("score.py", "--seed")
        self.run_cmd("build_site_data.py")
        self.run_cmd("make_prompt.py")
        self.run_cmd("validate_india_data.py")

        with open(ROOT / "site" / "data.json") as handle:
            payload = json.load(handle)

        self.assertGreaterEqual(len(payload), 20)
        for record in payload:
            self.assertEqual(record["country"], "India")
            self.assertIn("nco2004_3d", record)
            self.assertIn("sources", record)

    def test_markdown_pages_exist_for_seed_records(self):
        self.run_cmd("prepare_india_seed.py")
        with open(ROOT / "occupations.json") as handle:
            occupations = json.load(handle)
        missing = [
            row["slug"] for row in occupations
            if not (ROOT / "pages" / f"{row['slug']}.md").exists()
        ]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
