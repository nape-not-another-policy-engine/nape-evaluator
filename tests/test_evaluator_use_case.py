import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    EvaluateEvidenceResponse,
    TestInvocationRequest,
)
from nape_evaluator.domain.gateways import EvidenceLoadFailure
from nape_evaluator.domain.use_cases import (
    contextualize_messages,
    evaluate_evidence_against_tests,
    evaluate_request,
)


class TestEvaluatorUseCase(unittest.TestCase):
    def test_evaluate_request_returns_typed_response(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(
            evaluate=Mock(return_value=("pass", "ok"))
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[TestInvocationRequest.ready("./success_test.py", {})],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertIsInstance(actual, EvaluateEvidenceResponse)
        self.assertEqual(actual.count, 1)
        self.assertTrue(actual.results[0]["executed"])
        self.assertEqual(actual.results[0]["evidence_file"], "./evidence.json")
        self.assertEqual(actual.results[0]["test_parameters"], {})
        self.assertEqual(actual.results[0]["outcome"], "pass")
        self.assertEqual(actual.messages, [])

    def test_evaluate_evidence_against_tests_returns_pass_result(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            test_path = Path(tmp_dir) / "success_test.py"
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

            actual = evaluate_evidence_against_tests(
                str(evidence_path),
                [str(test_path)],
                evidence_gateway=Mock(
                    load_evidence_input=Mock(
                        return_value=(
                            {"status": "complete"},
                            {"evidence_type": "json", "schema_version": "2"},
                            [],
                        )
                    )
                ),
                test_of_detail_gateway=Mock(
                    load_test_of_detail=Mock(
                        return_value=Mock(evaluate=Mock(return_value=("pass", "ok")))
                    )
                ),
            )

        self.assertEqual(actual["results"][0]["outcome"], "pass")
        self.assertEqual(actual["results"][0]["reason"], "ok")
        self.assertTrue(actual["results"][0]["executed"])
        self.assertEqual(actual["results"][0]["evidence_file"], str(evidence_path))
        self.assertEqual(actual["results"][0]["test_parameters"], {})
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 1)

    def test_evaluate_evidence_against_tests_handles_missing_evidence(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = FileNotFoundError("missing")

        actual = evaluate_evidence_against_tests(
            "./missing.json",
            ["./test-a.py"],
            evidence_gateway=evidence_gateway,
            test_of_detail_gateway=Mock(),
        )

        self.assertEqual(len(actual["results"]), 1)
        self.assertFalse(actual["results"][0]["executed"])
        self.assertEqual(actual["results"][0]["outcome"], "error")
        self.assertEqual(actual["results"][0]["test"], "./test-a.py")
        self.assertEqual(actual["results"][0]["evidence_file"], "./missing.json")
        self.assertEqual(actual["results"][0]["test_parameters"], {})
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(actual["evaluator"]["messages"][0]["code"], "evidence_file_not_found")

    def test_evaluate_evidence_against_tests_continues_after_one_test_failure(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )

        def load_test(path):
            if path == "./raise_error.py":
                return Mock(evaluate=Mock(side_effect=RuntimeError("boom")))
            return Mock(evaluate=Mock(return_value=("pass", "ok")))

        test_gateway = Mock()
        test_gateway.load_test_of_detail.side_effect = load_test

        actual = evaluate_evidence_against_tests(
            "./evidence.json",
            ["./raise_error.py", "./pass_test.py"],
            evidence_gateway=evidence_gateway,
            test_of_detail_gateway=test_gateway,
        )

        self.assertEqual(actual["evaluator"]["summary"]["count"], 2)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 1)
        self.assertEqual(len(actual["results"]), 2)
        self.assertEqual(
            sorted((result["test"], result["executed"], result["outcome"]) for result in actual["results"]),
            [
                ("./pass_test.py", True, "pass"),
                ("./raise_error.py", False, "error"),
            ],
        )
        self.assertEqual(actual["evaluator"]["messages"][0]["code"], "test_execution_error")

    def test_evaluate_evidence_against_tests_returns_evaluator_execution_error_for_unexpected_failure(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = RuntimeError("unexpected boom")

        actual = evaluate_evidence_against_tests(
            "./evidence.json",
            ["./test-a.py"],
            evidence_gateway=evidence_gateway,
            test_of_detail_gateway=Mock(),
        )

        self.assertEqual(len(actual["results"]), 1)
        self.assertFalse(actual["results"][0]["executed"])
        self.assertEqual(actual["results"][0]["test"], "./test-a.py")
        self.assertEqual(actual["results"][0]["evidence_file"], "./evidence.json")
        self.assertEqual(actual["results"][0]["test_parameters"], {})
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["ran"], 0)
        self.assertEqual(actual["evaluator"]["summary"]["message_error"], 1)
        self.assertEqual(
            actual["evaluator"]["messages"][0]["code"],
            "evaluator_execution_error",
        )
        self.assertEqual(
            actual["evaluator"]["messages"][0]["evidence_file"],
            "./evidence.json",
        )
        self.assertIsNone(actual["evaluator"]["messages"][0]["test_file"])
        self.assertIsNone(actual["evaluator"]["messages"][0]["test_parameters_source"])

    def test_evaluate_request_handles_evidence_load_failure(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = EvidenceLoadFailure(
            "bad evidence",
            [{"level": "error", "source": "evaluator", "code": "evidence_load_error", "message": "bad evidence", "evidence_file": "./evidence.json", "test_file": None}],
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[TestInvocationRequest.ready("./test-a.py", {})],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 1)
        self.assertEqual(len(actual.results), 1)
        self.assertFalse(actual.results[0]["executed"])
        self.assertEqual(actual.results[0]["evidence_file"], "./evidence.json")
        self.assertEqual(actual.results[0]["test_parameters"], {})
        self.assertEqual(actual.messages[0]["code"], "evidence_load_error")
        self.assertEqual(actual.messages[0]["test_file"], "./test-a.py")

    def test_evaluate_request_contextualizes_shared_messages_for_each_test(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [
                {
                    "level": "warning",
                    "source": "evaluator",
                    "code": "missing_extension_text_fallback",
                    "message": "fallback",
                    "evidence_file": None,
                    "test_file": None,
                }
            ],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(
            evaluate=Mock(return_value=("pass", "ok"))
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence",
                test_invocations=[
                    TestInvocationRequest.ready("./test-a.py", {}),
                    TestInvocationRequest.ready("./test-b.py", {}),
                ],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(len(actual.results), 2)
        self.assertEqual(len(actual.messages), 2)
        self.assertEqual(actual.messages[0]["test_file"], "./test-a.py")
        self.assertEqual(actual.messages[1]["test_file"], "./test-b.py")

    def test_evaluate_request_converts_invalid_outcome_to_result_error(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(
            evaluate=Mock(return_value=("custom_status", "not used"))
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[TestInvocationRequest.ready("./bad-outcome.py", {})],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(actual.count, 1)
        self.assertEqual(len(actual.results), 1)
        self.assertTrue(actual.results[0]["executed"])
        self.assertEqual(actual.results[0]["evidence_file"], "./evidence.json")
        self.assertEqual(actual.results[0]["test_parameters"], {})
        self.assertEqual(actual.results[0]["outcome"], "error")
        self.assertIn("unsupported outcome", actual.results[0]["reason"])
        self.assertEqual(actual.messages, [])

    def test_evaluate_request_reports_missing_test_file(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.side_effect = FileNotFoundError("missing test")

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[TestInvocationRequest.ready("./missing-test.py", {})],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(len(actual.results), 1)
        self.assertFalse(actual.results[0]["executed"])
        self.assertEqual(actual.results[0]["test"], "./missing-test.py")
        self.assertEqual(actual.results[0]["test_parameters"], {})
        self.assertEqual(actual.messages[0]["code"], "test_file_not_found")
        self.assertEqual(actual.messages[0]["test_file"], "./missing-test.py")

    def test_evaluate_request_reports_test_import_error(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.side_effect = ImportError("bad import")

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[TestInvocationRequest.ready("./bad-test.py", {})],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(len(actual.results), 1)
        self.assertFalse(actual.results[0]["executed"])
        self.assertEqual(actual.results[0]["test"], "./bad-test.py")
        self.assertEqual(actual.results[0]["test_parameters"], {})
        self.assertEqual(actual.messages[0]["code"], "test_import_error")
        self.assertEqual(actual.messages[0]["test_file"], "./bad-test.py")

    def test_evaluate_request_repeats_evidence_load_failure_for_each_requested_test(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = EvidenceLoadFailure(
            "bad evidence",
            [
                {
                    "level": "error",
                    "source": "evaluator",
                    "code": "evidence_load_error",
                    "message": "bad evidence",
                    "evidence_file": "./evidence.json",
                    "test_file": None,
                }
            ],
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[
                    TestInvocationRequest.ready("./test-a.py", {}),
                    TestInvocationRequest.ready("./test-b.py", {}),
                ],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 2)
        self.assertEqual(len(actual.results), 2)
        self.assertEqual(
            [result["test"] for result in actual.results],
            ["./test-a.py", "./test-b.py"],
        )
        self.assertTrue(all(not result["executed"] for result in actual.results))
        self.assertEqual(len(actual.messages), 2)
        self.assertEqual(actual.messages[0]["test_file"], "./test-a.py")
        self.assertEqual(actual.messages[1]["test_file"], "./test-b.py")

    def test_evaluate_request_allows_zero_requested_tests_at_domain_level(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 0)
        self.assertEqual(actual.results, [])
        self.assertEqual(actual.messages, [])

    def test_evaluate_request_missing_evidence_with_zero_tests_returns_no_count_and_one_message(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = FileNotFoundError("missing")

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./missing.json",
                test_invocations=[],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 0)
        self.assertEqual(actual.results, [])
        self.assertEqual(len(actual.messages), 1)
        self.assertEqual(actual.messages[0]["code"], "evidence_file_not_found")
        self.assertIsNone(actual.messages[0]["test_file"])

    def test_evaluate_request_evidence_load_failure_with_zero_tests_returns_no_count_and_one_message(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.side_effect = EvidenceLoadFailure(
            "bad evidence",
            [
                {
                    "level": "error",
                    "source": "evaluator",
                    "code": "evidence_load_error",
                    "message": "bad evidence",
                    "evidence_file": "./evidence.json",
                    "test_file": None,
                }
            ],
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 0)
        self.assertEqual(actual.results, [])
        self.assertEqual(len(actual.messages), 1)
        self.assertEqual(actual.messages[0]["code"], "evidence_load_error")
        self.assertIsNone(actual.messages[0]["test_file"])

    def test_contextualize_messages_returns_empty_list_for_empty_input(self):
        actual = contextualize_messages([], "./evidence.json", "./test.py")

        self.assertEqual(actual, [])

    def test_evaluate_request_reports_blocked_test_parameter_invocation(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[
                    TestInvocationRequest.blocked(
                        "./threshold-test.py",
                        "test_parameter_shape_error",
                        "Test parameter input must be a top-level JSON object.",
                        test_parameters_source="./params.json",
                    )
                ],
            ),
            evidence_gateway,
            Mock(),
        )

        self.assertEqual(actual.count, 1)
        self.assertEqual(len(actual.results), 1)
        self.assertFalse(actual.results[0]["executed"])
        self.assertIsNone(actual.results[0]["test_parameters"])
        self.assertEqual(actual.messages[0]["code"], "test_parameter_shape_error")
        self.assertEqual(actual.messages[0]["test_file"], "./threshold-test.py")
        self.assertEqual(actual.messages[0]["test_parameters_source"], "./params.json")

    def test_evaluate_request_passes_test_parameters_to_test_of_detail(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        evaluate_mock = Mock(return_value=("pass", "ok"))
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(evaluate=evaluate_mock)

        actual = evaluate_request(
            EvaluateEvidenceRequest(
                evidence_path="./evidence.json",
                test_invocations=[
                    TestInvocationRequest.ready(
                        "./threshold-test.py",
                        {"minCoverage": 80},
                        test_parameters_source="./params.json",
                    )
                ],
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(actual.results[0]["test_parameters_source"], "./params.json")
        self.assertEqual(actual.results[0]["test_parameters"], {"minCoverage": 80})
        self.assertEqual(
            evaluate_mock.call_args.args,
            (
                {"status": "complete"},
                {"minCoverage": 80},
                {"evidence_type": "json", "schema_version": "2"},
            ),
        )

    def test_evaluate_response_to_cli_output_preserves_contract_shape(self):
        response = EvaluateEvidenceResponse(
            count=1,
            results=[
                {
                    "test": "a.py",
                    "evidence_file": "./evidence.json",
                    "test_parameters": {},
                    "test_parameters_source": None,
                    "executed": True,
                    "outcome": "pass",
                    "reason": "ok",
                }
            ],
            messages=[],
        )

        actual = response.to_cli_output()

        self.assertEqual(actual["results"][0]["test"], "a.py")
        self.assertEqual(actual["evaluator"]["summary"]["count"], 1)
        self.assertEqual(actual["evaluator"]["summary"]["pass"], 1)
