import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestJsonParsing(unittest.TestCase):
    def setUp(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.main_py = repo_root / "main.py"
        self.evidence_file = Path(__file__).resolve().parent / "evidence" / "author_verification.json"
        self.test_of_detail = Path(__file__).resolve().parent / "test_of_detail" / "verify_author_complete.py"

    def test_valid_json_load(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                json.dumps(
                    {
                        "test": str(self.test_of_detail),
                        "evaluations": [
                            {
                                "subject": {"name": "status", "data_type": "text"},
                                "criteria": {"equals": "complete"},
                            }
                        ],
                    }
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["true"], 1)
        self.assertTrue(output_json["results"][0]["execution"]["executed"])
        self.assertEqual(output_json["results"][0]["evidence"], str(self.evidence_file))
        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "true")
        self.assertEqual(
            output_json["results"][0]["result"]["reason"],
            "The author has achieved the status of complete.",
        )

    def test_json_result_changes_when_evaluation_input_changes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                json.dumps(
                    {
                        "test": str(self.test_of_detail),
                        "evaluations": [
                            {
                                "subject": {"name": "status", "data_type": "text"},
                                "criteria": {"equals": "approved"},
                            }
                        ],
                    }
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["false"], 1)
        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertEqual(
            output_json["results"][0]["result"]["reason"],
            "The author has not achieved the status of approved, their current status is 'complete'.",
        )
