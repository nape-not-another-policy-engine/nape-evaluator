import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestYamlPatternLibraryFixtures(unittest.TestCase):
    def setUp(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.main_py = repo_root / "main.py"
        self.evidence_dir = Path(__file__).resolve().parent / "evidence"
        self.test_dir = Path(__file__).resolve().parent / "test_of_detail"

    def _run_fixture(self, evidence_name, test_name, evaluations):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_dir / evidence_name),
                "--invoke",
                json.dumps(
                    {
                        "test": str(self.test_dir / test_name),
                        "evaluations": evaluations,
                    }
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_yaml_coverage_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "component_assurance.yaml",
            "verify_component_coverage_minimum.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 90},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("90.0", output_json["results"][0]["result"]["reason"])

    def test_yaml_invalid_fact_fixture_returns_inconclusive(self):
        output_json = self._run_fixture(
            "component_assurance_invalid_coverage.yaml",
            "verify_component_coverage_invalid_fact.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 80},
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["status"], "invalid"
        )
