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

    def assert_request_error_output(
        self,
        result,
        *,
        expected_code: str,
        expected_message_fragment: str,
        expected_affected_tests=None,
    ):
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["results"], [])
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(len(output_json["evaluator"]["messages"]), 1)
        message = output_json["evaluator"]["messages"][0]
        self.assertEqual(message["scope"], "request")
        self.assertEqual(message["level"], "error")
        self.assertEqual(message["code"], expected_code)
        self.assertIn(expected_message_fragment, message["message"])
        self.assertEqual(
            message["affected_tests"],
            expected_affected_tests if expected_affected_tests is not None else [],
        )

    def test_check_install(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py), "--check-install"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "NAPE Evaluator CLI is installed and working.")

    def test_no_arguments_return_zero_and_json_error_output(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assert_request_error_output(
            result,
            expected_code="cli_argument_error",
            expected_message_fragment="No evaluator invocation arguments were provided.",
        )

    def test_check_install_cannot_be_combined_with_v2_evaluation_args_and_returns_json_error(self):
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
        self.assert_request_error_output(
            result,
            expected_code="cli_argument_error",
            expected_message_fragment="--check-install cannot be combined with --evidence, --invoke, --invoke-file, or --request-file.",
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

    def test_invalid_invoke_json_returns_zero_and_json_error(self):
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
        self.assert_request_error_output(
            result,
            expected_code="request_json_decode_error",
            expected_message_fragment="Failed to decode --invoke value as JSON.",
        )

    def test_invalid_invoke_file_json_returns_zero_and_json_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            invoke_file = Path(tmp_dir) / "invoke.json"
            invoke_file.write_text("{bad json", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(self.evidence_file),
                    "--invoke-file",
                    str(invoke_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_request_error_output(
            result,
            expected_code="request_json_decode_error",
            expected_message_fragment=f"Failed to decode invoke file {invoke_file} as JSON.",
        )

    def test_direct_mode_missing_evidence_returns_zero_and_json_error(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--invoke",
                _status_invoke_json(str(self.json_test_file)),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assert_request_error_output(
            result,
            expected_code="cli_argument_error",
            expected_message_fragment="--evidence must be provided with --invoke or --invoke-file.",
        )

    def test_evidence_without_invokes_returns_zero_and_json_error(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assert_request_error_output(
            result,
            expected_code="cli_argument_error",
            expected_message_fragment="--evidence must be provided together with at least one --invoke or --invoke-file.",
        )

    def test_invalid_subject_name_returns_zero_and_json_error(self):
        invalid_request = json.dumps(
            {
                "test": str(self.json_test_file),
                "evaluations": [
                    {
                        "subject": {"name": "Status", "data_type": "text"},
                        "criteria": {"equals": "complete"},
                    }
                ],
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_file),
                "--invoke",
                invalid_request,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assert_request_error_output(
            result,
            expected_code="invalid_subject_name",
            expected_message_fragment="must be lowercase snake_case ASCII",
            expected_affected_tests=[str(self.json_test_file)],
        )

    def test_request_file_top_level_array_returns_zero_and_json_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_file = Path(tmp_dir) / "request.json"
            request_file.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(self.main_py), "--request-file", str(request_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_request_error_output(
            result,
            expected_code="invalid_request_packet",
            expected_message_fragment="--request-file must decode to a top-level JSON object.",
        )

    def test_request_file_invalid_json_returns_zero_and_json_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_file = Path(tmp_dir) / "request.json"
            request_file.write_text("{bad json", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(self.main_py), "--request-file", str(request_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assert_request_error_output(
            result,
            expected_code="request_json_decode_error",
            expected_message_fragment=f"Failed to decode request file {request_file} as JSON.",
        )

    def test_request_file_dash_invalid_json_returns_zero_and_json_error(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py), "--request-file", "-"],
            input="{bad json",
            capture_output=True,
            text=True,
            check=False,
        )

        self.assert_request_error_output(
            result,
            expected_code="request_json_decode_error",
            expected_message_fragment="Failed to decode stdin request JSON.",
        )

    def test_unknown_flag_returns_zero_and_json_error(self):
        result = subprocess.run(
            [sys.executable, str(self.main_py), "--unknown-flag"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assert_request_error_output(
            result,
            expected_code="cli_argument_error",
            expected_message_fragment="unrecognized arguments: --unknown-flag",
        )

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
        self.assertEqual(output_json["evaluator"]["summary"]["inconclusive"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertFalse(output_json["results"][0]["execution"]["executed"])
        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(output_json["evaluator"]["messages"][0]["scope"], "request")
        self.assertEqual(
            output_json["evaluator"]["messages"][0]["affected_tests"],
            [str(self.json_test_file)],
        )

    def test_multi_test_shared_warning_is_counted_once_as_request_scoped_event(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "author_verification"
            evidence_path.write_text('{"author":"Bill Bensing","status":"complete"}', encoding="utf-8")
            test_path = Path(tmp_dir) / "verify_status_from_text.py"
            test_path.write_text(
                "\n".join(
                    [
                        "import json",
                        "",
                        "def evaluate(evidence, evaluations, metadata):",
                        '    data = json.loads("".join(evidence))',
                        '    expected = evaluations[0]["criteria"]["equals"]',
                        '    status = data.get("status")',
                        '    fact = {"name": "status", "value": status, "value_type": "text", "status": "found" if status not in (None, "") else "not_found"}',
                        '    if fact["status"] != "found":',
                        '        return {"conclusion": "inconclusive", "facts": [fact], "reason": "Status could not be established."}',
                        "    if status == expected:",
                        '        return {"conclusion": "true", "facts": [fact], "reason": "Status matches."}',
                        '    return {"conclusion": "false", "facts": [fact], "reason": "Status does not match."}',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--invoke",
                    _status_invoke_json(str(test_path), expected_status="complete"),
                    "--invoke",
                    _status_invoke_json(str(test_path), expected_status="approved"),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 2)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 2)
        self.assertEqual(output_json["evaluator"]["summary"]["true"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["false"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_warning"], 1)
        self.assertEqual(output_json["evaluator"]["messages"][0]["scope"], "request")
        self.assertEqual(
            output_json["evaluator"]["messages"][0]["affected_tests"],
            [str(test_path), str(test_path)],
        )

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
