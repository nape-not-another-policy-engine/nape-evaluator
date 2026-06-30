import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCli(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.main_py = self.repo_root / "main.py"
        self.manual_test_dir = self.repo_root / "test"
        self.json_test_file = self.repo_root / "tests" / "json" / "test_of_detail" / "verify_author_complete.py"

    def test_check_install(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py), "--check-install"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "NAPE Evaluator CLI is installed and working.")

    def test_json_inconclusive_for_empty_status(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.manual_test_dir / "author_verification.json"),
                "--test",
                str(self.manual_test_dir / "verify_author_complete_2.py"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["outcome"], "inconclusive")
        self.assertEqual(
            output_json["reason"],
            "The expected data field 'status' does not contain a value.",
        )

    def test_invalid_json_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "invalid.json"
            evidence_path.write_text("{invalid json", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(self.json_test_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["outcome"], "error")
        self.assertIn("Error loading evidence:", output_json["reason"])
