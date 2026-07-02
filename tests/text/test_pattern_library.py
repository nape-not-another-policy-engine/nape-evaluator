import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestTextPatternLibraryFixtures(unittest.TestCase):
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

    def test_text_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "author_verification.txt",
            "verify_author_complete.py",
            [
                {
                    "subject": {"name": "status", "data_type": "text"},
                    "criteria": {"equals": "approved"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_text_ambiguous_status_fixture_returns_inconclusive(self):
        output_json = self._run_fixture(
            "author_verification_ambiguous_status.txt",
            "verify_author_complete_ambiguous.py",
            [
                {
                    "subject": {"name": "status", "data_type": "text"},
                    "criteria": {"equals": "complete"},
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["status"], "invalid"
        )
