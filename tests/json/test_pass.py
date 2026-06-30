import unittest
import json
import subprocess
import sys
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
                "--test",
                str(self.test_of_detail),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["outcome"], "pass")
        self.assertEqual(output_json["reason"], "The author has achieved the status of complete.")
