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

    def test_build_summary_counts_completed_conclusions_and_messages(self):
        results = [
            {
                "execution": {"executed": True, "status": "completed"},
                "result": {"conclusion": "true", "facts": [], "reason": "ok"},
            },
            {
                "execution": {"executed": True, "status": "completed"},
                "result": {"conclusion": "false", "facts": [], "reason": "not ok"},
            },
            {
                "execution": {"executed": False, "status": "blocked"},
                "result": None,
            },
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
                "true": 1,
                "false": 1,
                "inconclusive": 0,
                "error": 0,
                "message_count": 2,
                "message_info": 0,
                "message_warning": 1,
                "message_error": 1,
            },
        )

    def test_build_cli_output_nests_messages_and_summary_under_evaluator(self):
        messages = [build_message("error", "error_code", "error text")]
        results = [
            {
                "test": "test-a.py",
                "evidence": "./evidence.json",
                "evaluations": [],
                "execution": {"executed": True, "status": "completed"},
                "result": {"conclusion": "true", "facts": [], "reason": "Reason text"},
            }
        ]

        actual = build_cli_output(1, results, messages)

        self.assertIn("results", actual)
        self.assertIn("evaluator", actual)
        self.assertEqual(actual["evaluator"]["messages"], messages)
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["true"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["message_error"], 1)
