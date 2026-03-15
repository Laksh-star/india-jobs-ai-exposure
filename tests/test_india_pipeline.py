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

        self.assertIn("canonical_rows", payload)
        self.assertIn("display_nodes", payload)
        self.assertIn("meta", payload)
        self.assertGreaterEqual(len(payload["canonical_rows"]), 20)
        self.assertGreaterEqual(payload["meta"]["display_leaf_count"], 90)
        self.assertLessEqual(payload["meta"]["display_leaf_count"], 110)

        for record in payload["canonical_rows"]:
            self.assertEqual(record["country"], "India")
            self.assertIn("nco2004_3d", record)
            self.assertIn("sources", record)

        kinds = {node["node_kind"] for node in payload["display_nodes"]}
        self.assertEqual(kinds, {"major_group", "nco_group", "role"})

    def test_markdown_pages_exist_for_seed_records(self):
        self.run_cmd("prepare_india_seed.py")
        with open(ROOT / "occupations.json") as handle:
            occupations = json.load(handle)
        missing = [
            row["slug"] for row in occupations
            if not (ROOT / "pages" / f"{row['slug']}.md").exists()
        ]
        self.assertEqual(missing, [])

    def test_display_role_taxonomy_shares_are_valid(self):
        with open(ROOT / "india" / "display_roles.json") as handle:
            roles = json.load(handle)

        by_parent = {}
        for role in roles:
            by_parent.setdefault(role["parent_nco2004_3d"], []).append(role)

        self.assertEqual(len(by_parent), 28)
        for parent, items in by_parent.items():
            self.assertGreaterEqual(len(items), 3)
            self.assertLessEqual(sum(role["share"] for role in items), 1.0)


if __name__ == "__main__":
    unittest.main()
