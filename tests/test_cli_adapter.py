import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from nape_evaluator.application.io import cli
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceResponse,
    TestInvocationRequest,
)


class TestCliAdapter(unittest.TestCase):
    def test_parse_args_accepts_repeated_test_arguments(self):
        args = cli.parse_args(
            [
                "--evidence",
                "./evidence.json",
                "--test",
                "./test-a.py",
                "--test",
                "./test-b.py",
            ]
        )

        self.assertEqual(args.evidence, "./evidence.json")
        self.assertEqual(args.test, ["./test-a.py", "./test-b.py"])
        self.assertFalse(args.check_install)

    def test_parse_args_accepts_repeated_parameter_files(self):
        args = cli.parse_args(
            [
                "--evidence",
                "./evidence.json",
                "--test",
                "./test-a.py",
                "--test-parameters-file",
                "./params-a.json",
            ]
        )

        self.assertEqual(args.test_parameters_file, ["./params-a.json"])

    def test_parse_args_rejects_missing_paired_argument(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr), self.assertRaises(SystemExit) as context:
            cli.parse_args(["--evidence", "./evidence.json"])

        self.assertEqual(context.exception.code, 2)
        self.assertIn("--evidence and --test must be provided together.", stderr.getvalue())

    def test_parse_args_rejects_check_install_combined_with_evaluation_args(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr), self.assertRaises(SystemExit) as context:
            cli.parse_args(
                [
                    "--check-install",
                    "--evidence",
                    "./evidence.json",
                    "--test",
                    "./test.py",
                ]
            )

        self.assertEqual(context.exception.code, 2)
        self.assertIn(
            "--check-install cannot be combined with --evidence, --test, or --test-parameters-file.",
            stderr.getvalue(),
        )

    def test_parse_args_rejects_parameter_count_mismatch(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr), self.assertRaises(SystemExit) as context:
            cli.parse_args(
                [
                    "--evidence",
                    "./evidence.json",
                    "--test",
                    "./test-a.py",
                    "--test",
                    "./test-b.py",
                    "--test-parameters-file",
                    "./params-a.json",
                ]
            )

        self.assertEqual(context.exception.code, 2)
        self.assertIn(
            "--test-parameters-file must be omitted or repeated once per --test.",
            stderr.getvalue(),
        )

    def test_parse_args_rejects_no_arguments(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr), self.assertRaises(SystemExit) as context:
            cli.parse_args([])

        self.assertEqual(context.exception.code, 2)
        self.assertIn("usage:", stderr.getvalue().lower())

    def test_run_cli_check_install_prints_message(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = cli.run_cli(["--check-install"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "NAPE Evaluator CLI is installed and working.")

    def test_run_cli_prints_json_output(self):
        stdout = io.StringIO()

        with patch(
            "nape_evaluator.application.io.cli.evaluate_request",
            return_value=EvaluateEvidenceResponse(
                count=0,
                results=[],
                messages=[],
            ),
        ) as mock_use_case, redirect_stdout(stdout):
            exit_code = cli.run_cli(
                [
                    "--evidence",
                    "./evidence.json",
                    "--test",
                    "./test.py",
                ]
            )

        self.assertEqual(exit_code, 0)
        request = mock_use_case.call_args.args[0]
        self.assertEqual(request.evidence_path, "./evidence.json")
        self.assertEqual(
            request.test_invocations,
            [TestInvocationRequest.ready("./test.py", {})],
        )
        self.assertEqual(
            stdout.getvalue().strip(),
            '{"results": [], "evaluator": {"messages": [], "summary": {"count": 0, "ran": 0, "pass": 0, "fail": 0, "inconclusive": 0, "error": 0, "message_count": 0, "message_info": 0, "message_warning": 0, "message_error": 0}}}',
        )
