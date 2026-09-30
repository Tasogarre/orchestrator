"""Offline integrity checks, not comparative model-performance evaluations."""

from pathlib import Path
import json
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class PublicPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/results.json").read_text())

    def test_final_accounting_has_no_double_counted_subsets(self):
        usage = self.data["research_and_testing"]
        self.assertEqual(usage["total_tokens"], 345097261)
        self.assertEqual(usage["calls"], 426)
        self.assertEqual(usage["input_tokens"] + usage["output_tokens"],
                         usage["total_tokens"])
        self.assertEqual(usage["cached_input_tokens"] +
                         usage["uncached_input_tokens"], usage["input_tokens"])
        self.assertLessEqual(usage["reasoning_output_tokens"],
                             usage["output_tokens"])
        self.assertIn("Excludes the main conversation", usage["scope"])

    def test_final_diagnostics_match_published_rounded_claims(self):
        rows = self.data["results"]
        self.assertEqual(len(rows), 2)
        for row, saving, time in zip(rows, (34.8, 30.7), (34.3, 95.6)):
            tactic, direct = row["treatment"], row["direct"]
            computed = 100 * (1 - tactic["api_usd"] / direct["api_usd"])
            slower = 100 * (tactic["wall_seconds"] / direct["wall_seconds"] - 1)
            self.assertAlmostEqual(computed, row["cost_saving_percent"])
            self.assertAlmostEqual(slower, row["model_stage_time_increase_percent"])
            self.assertEqual(round(computed, 1), saving)
            self.assertEqual(round(slower, 1), time)
            self.assertEqual((tactic["quality"], direct["quality"]), (100, 100))
            self.assertEqual((tactic["severe_defects"], direct["severe_defects"]),
                             (0, 0))
            self.assertTrue(tactic["pass"] and direct["pass"])
        readme = (ROOT / "README.md").read_text()
        self.assertIn("345,097,261", readme)
        self.assertIn("not executions of the published automatic-routing skill", readme)
        self.assertIn("Results are not guaranteed", readme)

    def test_packaged_relative_links_exist(self):
        paths = [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "AGENTS.md"]
        paths.extend((ROOT / "references").glob("*.md"))
        for source in paths:
            for target in re.findall(r"\]\(([^)]+)\)", source.read_text()):
                if target.startswith(("https://", "http://", "#")):
                    continue
                target = target.split("#")[0]
                self.assertTrue((source.parent / target).is_file(),
                                f"{source.name}: missing {target}")

    def test_no_personal_paths_or_credential_shapes_in_payload(self):
        files = [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "AGENTS.md",
                 ROOT / "docs/results.json"]
        for folder in ("references", "scripts", "agents", "assets"):
            files.extend(p for p in (ROOT / folder).rglob("*") if p.is_file())
        patterns = (
            r"/Users/[A-Za-z0-9_-]+/",
            r"/home/[A-Za-z0-9_-]+/",
            r"gh[pousr]_[A-Za-z0-9]{30,}",
            r"sk-[A-Za-z0-9]{30,}",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            r"https://[^\s/]+\.priv\.",
        )
        for path in files:
            content = path.read_text()
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, content), path.name)

    def test_banner_is_self_contained_accessible_svg(self):
        svg = ET.parse(ROOT / "assets/orchestrator.svg").getroot()
        ns = "{http://www.w3.org/2000/svg}"
        self.assertIsNotNone(svg.find(ns + "title"))
        self.assertIsNotNone(svg.find(ns + "desc"))
        for element in svg.iter():
            self.assertNotIn(element.tag, (ns + "script", ns + "foreignObject"))
            for attribute, value in element.attrib.items():
                self.assertFalse(attribute.lower().startswith("on"))
                self.assertFalse(value.startswith(("http://", "https://")))


if __name__ == "__main__":
    unittest.main()
