import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from nape_evaluator.application.io import cli
from nape_evaluator.application.io.cli import CliInvocationError
from nape_evaluator.domain.use_case_models import EvaluateEvidenceResponse


def _completed_result():
    return {
        "test": "./test.py",
        "evidence": "./evidence.json",
        "evaluations": [],
        "execution": {"executed": True, "status": "completed"},
        "result": {"conclusion": "true", "facts": [], "reason": "ok"},
    }


class TestCliAdapter(unittest.TestCase):
    def test_parse_args_accepts_repeated_invoke_arguments(self):
        args = cli.parse_args(
            [
                "--evidence",
                "./evidence.json",
                "--invoke",
                '{"test":"./test-a.py","evaluations":[]}',
                "--invoke",
                '{"test":"./test-b.py","evaluations":[]}',
            ]
        )

        self.assertEqual(args.evidence, "./evidence.json")
        self.assertEqual(
            args.invoke,
            [
                '{"test":"./test-a.py","evaluations":[]}',
                '{"test":"./test-b.py","evaluations":[]}',
            ],
        )
        self.assertFalse(args.check_install)

    def test_parse_args_accepts_request_file(self):
        args = cli.parse_args(["--request-file", "./request.json"])
        self.assertEqual(args.request_file, "./request.json")

    def test_parse_args_rejects_mixing_request_file_and_direct_flags(self):
        with self.assertRaises(CliInvocationError) as context:
            cli.parse_args(
                [
                    "--request-file",
                    "./request.json",
                    "--evidence",
                    "./evidence.json",
                    "--invoke",
                    '{"test":"./test-a.py","evaluations":[]}',
                ]
            )

        self.assertEqual(context.exception.code, "cli_argument_error")
        self.assertIn(
            "--request-file cannot be combined with --evidence, --invoke, or --invoke-file.",
            str(context.exception),
        )

    def test_parse_args_rejects_no_arguments(self):
        with self.assertRaises(CliInvocationError) as context:
            cli.parse_args([])

        self.assertEqual(context.exception.code, "cli_argument_error")
        self.assertIn(
            "No evaluator invocation arguments were provided.",
            str(context.exception),
        )

    def test_parse_args_rejects_unknown_flag_with_bounded_cli_error(self):
        with self.assertRaises(CliInvocationError) as context:
            cli.parse_args(["--unknown-flag"])

        self.assertEqual(context.exception.code, "cli_argument_error")
        self.assertIn("unrecognized arguments: --unknown-flag", str(context.exception))

    def test_run_cli_check_install_prints_message(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = cli.run_cli(["--check-install"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "NAPE Evaluator CLI is installed and working.")

    def test_run_cli_builds_v2_request_from_invoke(self):
        stdout = io.StringIO()

        with patch(
            "nape_evaluator.application.io.cli.evaluate_request",
            return_value=EvaluateEvidenceResponse(
                count=1,
                results=(_completed_result(),),
                messages=(),
            ),
        ) as mock_use_case, redirect_stdout(stdout):
            exit_code = cli.run_cli(
                [
                    "--evidence",
                    "./evidence.json",
                    "--invoke",
                    '{"test":"./test.py","evaluations":[{"subject":{"name":"coverage","data_type":"number"},"criteria":{"minimum":80}}]}',
                ]
            )

        self.assertEqual(exit_code, 0)
        request = mock_use_case.call_args.args[0]
        self.assertEqual(request.evidence_path, "./evidence.json")
        self.assertEqual(len(request.test_invocations), 1)
        self.assertEqual(request.test_invocations[0].test_path, "./test.py")
        self.assertEqual(
            request.test_invocations[0].evaluations_as_dicts(),
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 80},
                }
            ],
        )
        self.assertIn('"true": 1', stdout.getvalue())

    def test_run_cli_returns_bounded_json_for_argument_error(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = cli.run_cli([])

        self.assertEqual(exit_code, 0)
        self.assertIn('"results": []', stdout.getvalue())
        self.assertIn('"code": "cli_argument_error"', stdout.getvalue())
