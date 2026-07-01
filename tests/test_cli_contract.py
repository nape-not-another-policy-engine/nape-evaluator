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
        self.manual_test_dir = self.repo_root / "tests" / "manual"
        self.json_test_file = self.repo_root / "tests" / "json" / "test_of_detail" / "verify_author_complete.py"
        self.empty_status_evidence = self.repo_root / "tests" / "json" / "evidence" / "author_verification_empty_status.json"

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

    def test_check_install_cannot_be_combined_with_evaluation_args(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--check-install",
                "--evidence",
                str(self.empty_status_evidence),
                "--test",
                str(self.json_test_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn(
            "--check-install cannot be combined with --evidence, --test, or --test-parameters-file.",
            result.stderr,
        )

    def test_json_inconclusive_for_empty_status(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.empty_status_evidence),
                "--test",
                str(self.json_test_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["inconclusive"], 1)
        self.assertTrue(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(self.empty_status_evidence))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["results"][0]["outcome"], "inconclusive")
        self.assertIsNone(output_json["results"][0]["test_parameters_source"])
        self.assertEqual(
            output_json["results"][0]["reason"],
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
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test"], str(self.json_test_file))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["evaluator"]["messages"][0]["level"], "error")
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "evidence_load_error")
        self.assertIn("Error loading evidence:", output_json["evaluator"]["messages"][0]["message"])
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(self.json_test_file))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])

    def test_missing_evidence_returns_file_not_found_error(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.manual_test_dir / "missing.json"),
                "--test",
                str(self.json_test_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(self.manual_test_dir / "missing.json"))
        self.assertEqual(output_json["results"][0]["test"], str(self.json_test_file))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "evidence_file_not_found")
        self.assertIn("Unable to find the file(s) for evaluation.", output_json["evaluator"]["messages"][0]["message"])
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(self.manual_test_dir / "missing.json"))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(self.json_test_file))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])

    def test_unhandled_test_exception_returns_json_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "raise_error.py"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    raise RuntimeError('boom')",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["error"], 0)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["test"], str(test_path))
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "test_execution_error")
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(test_path))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])

    def test_multiple_tests_return_results_array(self):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.empty_status_evidence),
                "--test",
                str(self.json_test_file),
                "--test",
                str(self.json_test_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 2)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 2)
        self.assertEqual(len(output_json["results"]), 2)
        self.assertTrue(all(result["executed"] for result in output_json["results"]))
        self.assertTrue(all(result["test_parameters"] == {} for result in output_json["results"]))
        self.assertEqual(output_json["results"][0]["outcome"], "inconclusive")
        self.assertEqual(output_json["results"][1]["outcome"], "inconclusive")
        self.assertEqual(output_json["evaluator"]["summary"]["inconclusive"], 2)

    def test_multiple_tests_continue_after_one_failure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            failing_test_path = Path(tmp_dir) / "raise_error.py"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")
            failing_test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    raise RuntimeError('boom')",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(failing_test_path),
                    "--test",
                    str(self.json_test_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 2)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(len(output_json["results"]), 2)
        self.assertEqual(
            sorted((result["test"], result["executed"], result["outcome"]) for result in output_json["results"]),
            [
                (str(self.json_test_file), True, "pass"),
                (str(failing_test_path), False, "error"),
            ],
        )
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "test_execution_error")
        self.assertEqual(output_json["evaluator"]["summary"]["error"], 0)
        self.assertEqual(output_json["evaluator"]["summary"]["pass"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(failing_test_path))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])

    def test_missing_extension_emits_warning_message(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence"
            test_path = Path(tmp_dir) / "text_test.py"
            evidence_path.write_text("hello\n", encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    if metadata.get('evidence_type') != 'text':",
                        "        return 'error', 'wrong type'",
                        "    return 'pass', 'Text evaluated.'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertTrue(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["results"][0]["outcome"], "pass")
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "missing_extension_text_fallback")
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(test_path))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])
        self.assertEqual(output_json["evaluator"]["summary"]["message_warning"], 1)

    def test_unknown_extension_binary_file_emits_warning_and_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "image.png"
            evidence_path.write_bytes(b"\x89PNG\r\n\x1a\n")

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
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test"], str(self.json_test_file))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "unprocessable_evidence_type")
        self.assertEqual(output_json["evaluator"]["messages"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_file"], str(self.json_test_file))
        self.assertIsNone(output_json["evaluator"]["messages"][0]["test_parameters_source"])
        self.assertEqual(len(output_json["evaluator"]["messages"]), 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 1)

    def test_invalid_test_outcome_is_normalized_to_result_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "bad_outcome.py"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    return 'custom_status', 'bad status'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["error"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["message_error"], 0)
        self.assertTrue(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test_parameters"], {})
        self.assertEqual(output_json["results"][0]["outcome"], "error")
        self.assertIsNone(output_json["results"][0]["test_parameters_source"])
        self.assertIn("unsupported outcome", output_json["results"][0]["reason"])

    def test_test_parameter_file_is_passed_to_test(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "threshold.py"
            params_path = Path(tmp_dir) / "params.json"
            evidence_path.write_text('{"coverage": 85}', encoding="utf-8")
            params_path.write_text('{"minCoverage": 80}', encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    if test_parameters.get('minCoverage') == 80:",
                        "        return 'pass', 'Threshold matched.'",
                        "    return 'fail', 'Threshold mismatch.'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                    "--test-parameters-file",
                    str(params_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(output_json["results"][0]["outcome"], "pass")
        self.assertTrue(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test_parameters"], {"minCoverage": 80})
        self.assertEqual(output_json["results"][0]["test_parameters_source"], str(params_path))

    def test_missing_test_parameter_file_blocks_only_that_invocation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "threshold.py"
            params_path = Path(tmp_dir) / "missing-params.json"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    return 'pass', 'ok'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                    "--test-parameters-file",
                    str(params_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test"], str(test_path))
        self.assertIsNone(output_json["results"][0]["test_parameters"])
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "test_parameter_file_not_found")
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_parameters_source"], str(params_path))

    def test_invalid_test_parameter_shape_blocks_only_that_invocation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "threshold.py"
            params_path = Path(tmp_dir) / "params.json"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")
            params_path.write_text('["not-an-object"]', encoding="utf-8")
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, test_parameters, metadata):",
                        "    return 'pass', 'ok'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.main_py),
                    "--evidence",
                    str(evidence_path),
                    "--test",
                    str(test_path),
                    "--test-parameters-file",
                    str(params_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        output_json = json.loads(result.stdout)
        self.assertEqual(output_json["evaluator"]["summary"]["count"], 1)
        self.assertEqual(output_json["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(len(output_json["results"]), 1)
        self.assertFalse(output_json["results"][0]["executed"])
        self.assertEqual(output_json["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(output_json["results"][0]["test"], str(test_path))
        self.assertIsNone(output_json["results"][0]["test_parameters"])
        self.assertEqual(output_json["evaluator"]["messages"][0]["code"], "test_parameter_shape_error")
        self.assertEqual(output_json["evaluator"]["messages"][0]["test_parameters_source"], str(params_path))
