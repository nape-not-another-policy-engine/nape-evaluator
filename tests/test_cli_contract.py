import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _status_invoke_json(test_path: str, expected_status: str = "complete"):
    return json.dumps(
        {
            "test": test_path,
            "evaluations": [
                {
                    "subject": {"name": "status", "data_type": "text"},
                    "criteria": {"equals": expected_status},
                }
            ],
        }
    )


class TestCli(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.main_py = self.repo_root / "main.py"
        self.json_test_file = (
            self.repo_root / "tests" / "json" / "test_of_detail" / "verify_author_complete.py"
        )
        self.evidence_file = (
            self.repo_root / "tests" / "json" / "evidence" / "author_verification.json"
        )
        self.empty_status_evidence = (
            self.repo_root
            / "tests"
            / "json"
            / "evidence"
            / "author_verification_empty_status.json"
        )

    def test_check_install(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py), "--check-install"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "NAPE Evaluator CLI is installed and working.")

    def test_no_arguments_prints_usage_and_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage:", result.stderr.lower())

    def test_check_install_cannot_be_combined_with_v2_evaluation_args(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--check-install",
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                _status_invoke_json(str(self.json_test_file)),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "--check-install cannot be combined with --evidence, --invoke, --invoke-file, or --request-file.",
            result.stderr,
        )

    def test_direct_invoke_returns_true_result(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                _status_invoke_json(str(self.json_test_file)),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["true"], 1)
        self.assertEqual(output_json["results"][0]["test"], str(self.json_test_file))
        self.assertEqual(output_json["results"][0]["evidence"], str(self.evidence_file))
        self.assertTrue(output_json["results"][0]["execution"]["executed"])
        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "true")

    def test_direct_invoke_uses_evaluation_input_for_result(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                _status_invoke_json(str(self.json_test_file), expected_status="approved"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["false"], 1)
        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_request_file_dash_reads_full_request_from_stdin(self):
        request_packet = json.dumps(
            {
                "evidence": str(self.evidence_file),
                "tests": [
                    json.loads(_status_invoke_json(str(self.json_test_file))),
                ],
            }
        )

        result = subprocess.run(
            [sys.executable, str(self.main_py), "--request-file", "-"],
            input=request_packet,
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["true"], 1)

    def test_empty_status_returns_inconclusive(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.empty_status_evidence),
                "--invoke",
                _status_invoke_json(str(self.json_test_file)),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["inconclusive"], 1)
        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "inconclusive")

    def test_invalid_invoke_json_returns_parse_error(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                "{bad json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Failed to decode --invoke value as JSON.", result.stderr)

    def test_missing_evidence_returns_blocked_result(self):
        missing_evidence = self.repo_root / "tests" / "manual" / "missing.json"
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(missing_evidence),
                "--invoke",
                _status_invoke_json(str(self.json_test_file)),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertFalse(output_json["results"][0]["execution"]["executed"])
        self.assertIsNone(output_json["results"][0]["result"])

    def test_request_file_reads_from_json_file(self):
        request_packet = {
            "evidence": str(self.evidence_file),
            "tests": [json.loads(_status_invoke_json(str(self.json_test_file)))],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_file = Path(tmp_dir) / "request.json"
            request_file.write_text(json.dumps(request_packet), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(self.main_py), "--request-file", str(request_file)],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["true"], 1)
