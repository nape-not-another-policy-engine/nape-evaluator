import unittest

from nape_evaluator.application.io.output_contract import (
    build_cli_output,
    build_message,
    build_summary,
)


class TestOutputContract(unittest.TestCase):
    def test_build_message_returns_full_public_message_shape(self):
        actual = build_message(
            "warning",
            "missing_extension_text_fallback",
            "Evidence file had no extension and was evaluated as text.",
            evidence_file="./evidence",
            test_file=None,
            scope="request",
            affected_tests=["./test-a.py", "./test-b.py"],
            stack_trace=None,
        )

        self.assertEqual(
            actual,
            {
                "scope": "request",
                "level": "warning",
                "source": "evaluator",
                "code": "missing_extension_text_fallback",
                "message": "Evidence file had no extension and was evaluated as text.",
                "evidence_file": "./evidence",
                "test_file": None,
                "affected_tests": ["./test-a.py", "./test-b.py"],
                "stack_trace": None,
            },
        )

    def test_build_summary_counts_completed_and_blocked_inconclusive_results(self):
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
                "result": {
                    "conclusion": "inconclusive",
                    "facts": [],
                    "reason": "blocked",
                },
            },
        ]
        messages = [
            build_message(
                "warning",
                "warning_code",
                "warning text",
                evidence_file="./evidence",
                test_file=None,
                scope="request",
                affected_tests=["./test-a.py", "./test-b.py", "./test-c.py"],
            ),
            build_message(
                "error",
                "error_code",
                "error text",
                evidence_file="./evidence",
                test_file="./test-c.py",
                scope="test",
                affected_tests=None,
            ),
        ]

        actual = build_summary(3, results, messages)

        self.assertEqual(
            actual,
            {
                "count": 3,
                "ran": 2,
                "true": 1,
                "false": 1,
                "inconclusive": 1,
                "message_count": 2,
                "message_info": 0,
                "message_warning": 1,
                "message_error": 1,
            },
        )

    def test_build_cli_output_nests_messages_and_summary_under_evaluator(self):
        messages = [
            build_message(
                "error",
                "error_code",
                "error text",
                evidence_file="./evidence.json",
                test_file="./test-a.py",
                scope="test",
                affected_tests=None,
            )
        ]
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

    def test_build_summary_counts_distinct_request_scoped_events_once(self):
        results = [
            {
                "execution": {"executed": True, "status": "completed"},
                "result": {"conclusion": "true", "facts": [], "reason": "ok"},
            },
            {
                "execution": {"executed": True, "status": "completed"},
                "result": {"conclusion": "false", "facts": [], "reason": "not ok"},
            },
        ]
        messages = [
            build_message(
                "warning",
                "missing_extension_text_fallback",
                "fallback",
                evidence_file="./evidence",
                test_file=None,
                scope="request",
                affected_tests=["./test-a.py", "./test-b.py"],
            )
        ]

        actual = build_summary(2, results, messages)

        self.assertEqual(actual["message_count"], 1)
        self.assertEqual(actual["message_warning"], 1)
        self.assertEqual(actual["true"], 1)
        self.assertEqual(actual["false"], 1)
