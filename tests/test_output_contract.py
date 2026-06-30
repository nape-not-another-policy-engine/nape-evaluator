import unittest

from nape_evaluator.application.io.output_contract import (
    build_cli_output,
    build_message,
    build_summary,
)


class TestOutputContract(unittest.TestCase):
    def test_build_message_sets_evaluator_source(self):
        actual = build_message(
            "warning",
            "missing_extension_text_fallback",
            "Evidence file had no extension and was evaluated as text.",
            evidence_file="./evidence",
            test_file="./text_test.py",
        )

        self.assertEqual(
            actual,
            {
                "level": "warning",
                "source": "evaluator",
                "code": "missing_extension_text_fallback",
                "message": "Evidence file had no extension and was evaluated as text.",
                "evidence_file": "./evidence",
                "test_file": "./text_test.py",
            },
        )

    def test_build_summary_counts_results_and_messages_separately(self):
        results = [
            {"outcome": "pass"},
            {"outcome": "error"},
        ]
        messages = [
            build_message("warning", "warning_code", "warning text"),
            build_message("error", "error_code", "error text"),
        ]

        actual = build_summary(3, results, messages)

        self.assertEqual(
            actual,
            {
                "count": 3,
                "ran": 2,
                "pass": 1,
                "fail": 0,
                "inconclusive": 0,
                "error": 1,
                "message_count": 2,
                "message_info": 0,
                "message_warning": 1,
                "message_error": 1,
            },
        )

    def test_build_cli_output_nests_messages_and_summary_under_evaluator(self):
        messages = [build_message("error", "error_code", "error text")]

        actual = build_cli_output(
            1,
            [{"test": "test-a.py", "outcome": "pass", "reason": "Reason text"}],
            messages,
        )

        self.assertIn("results", actual)
        self.assertIn("evaluator", actual)
        self.assertEqual(actual["evaluator"]["messages"], messages)
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["pass"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["message_error"], 1)

    def test_build_summary_counts_info_messages_separately_from_results(self):
        actual = build_summary(
            1,
            [{"outcome": "inconclusive"}],
            [build_message("info", "info_code", "info text")],
        )

        self.assertEqual(actual["count"], 1)
        self.assertEqual(actual["ran"], 1)
        self.assertEqual(actual["inconclusive"], 1)
        self.assertEqual(actual["message_count"], 1)
        self.assertEqual(actual["message_info"], 1)

    def test_build_summary_ignores_unknown_result_outcomes(self):
        actual = build_summary(
            1,
            [{"outcome": "custom"}],
            [],
        )

        self.assertEqual(actual["count"], 1)
        self.assertEqual(actual["ran"], 1)
        self.assertEqual(actual["pass"], 0)
        self.assertEqual(actual["fail"], 0)
        self.assertEqual(actual["inconclusive"], 0)
        self.assertEqual(actual["error"], 0)

    def test_build_summary_ignores_unknown_message_levels(self):
        actual = build_summary(
            0,
            [],
            [{"level": "debug"}],
        )

        self.assertEqual(actual["message_count"], 1)
        self.assertEqual(actual["message_info"], 0)
        self.assertEqual(actual["message_warning"], 0)
        self.assertEqual(actual["message_error"], 0)
