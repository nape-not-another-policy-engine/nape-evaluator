import unittest
from unittest.mock import Mock

from nape_evaluator.domain.gateways import EvidenceLoadFailure
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    EvaluateEvidenceResponse,
)
from nape_evaluator.domain.use_cases import contextualize_messages, evaluate_request


def _request(raw_tests=None):
    return (
        EvaluateEvidenceRequest.builder()
        .evidence_path("./evidence.json")
        .raw_tests(
            raw_tests
            or [
                {
                    "test": "./success_test.py",
                    "evaluations": [
                        {
                            "subject": {"name": "status", "data_type": "text"},
                            "criteria": {"equals": "complete"},
                        }
                    ],
                }
            ]
        )
        .try_build()
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
            evaluate=Mock(
                return_value={
                    "conclusion": "true",
                    "facts": [],
                    "reason": "ok",
                }
            )
        )

        actual = evaluate_request(_request(), evidence_gateway, test_gateway)

        self.assertIsInstance(actual, EvaluateEvidenceResponse)
        self.assertEqual(actual.count, 1)
        self.assertTrue(actual.results[0]["execution"]["executed"])
        self.assertEqual(actual.results[0]["evidence"], "./evidence.json")
        self.assertEqual(actual.results[0]["result"]["conclusion"], "true")
        self.assertEqual(actual.messages, ())

    def test_evaluate_request_normalizes_invalid_test_result_to_completed_error(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(
            evaluate=Mock(return_value=("not", "valid"))
        )

        actual = evaluate_request(_request(), evidence_gateway, test_gateway)

        self.assertTrue(actual.results[0]["execution"]["executed"])
        self.assertEqual(actual.results[0]["execution"]["status"], "completed")
        self.assertEqual(actual.results[0]["result"]["conclusion"], "error")
        self.assertIn("invalid result contract", actual.results[0]["result"]["reason"])

    def test_evaluate_request_handles_evidence_load_failure(self):
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

        actual = evaluate_request(_request(), evidence_gateway, Mock())

        self.assertEqual(actual.count, 1)
        self.assertFalse(actual.results[0]["execution"]["executed"])
        self.assertIsNone(actual.results[0]["result"])
        self.assertEqual(actual.messages[0]["code"], "evidence_load_error")
        self.assertEqual(actual.messages[0]["test_file"], "./success_test.py")

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
            evaluate=Mock(
                return_value={
                    "conclusion": "true",
                    "facts": [],
                    "reason": "ok",
                }
            )
        )

        actual = evaluate_request(
            _request(
                [
                    {
                        "test": "./test-a.py",
                        "evaluations": [],
                    },
                    {
                        "test": "./test-b.py",
                        "evaluations": [],
                    },
                ]
            ),
            evidence_gateway,
            test_gateway,
        )

        self.assertEqual(len(actual.results), 2)
        self.assertEqual(len(actual.messages), 2)
        self.assertEqual(actual.messages[0]["test_file"], "./test-a.py")
        self.assertEqual(actual.messages[1]["test_file"], "./test-b.py")

    def test_evaluate_request_blocks_failed_test_execution(self):
        evidence_gateway = Mock()
        evidence_gateway.load_evidence_input.return_value = (
            {"status": "complete"},
            {"evidence_type": "json", "schema_version": "2"},
            [],
        )
        test_gateway = Mock()
        test_gateway.load_test_of_detail.return_value = Mock(
            evaluate=Mock(side_effect=RuntimeError("boom"))
        )

        actual = evaluate_request(_request(), evidence_gateway, test_gateway)

        self.assertFalse(actual.results[0]["execution"]["executed"])
        self.assertIsNone(actual.results[0]["result"])
        self.assertEqual(actual.messages[0]["code"], "test_execution_error")


class TestMessageContextualization(unittest.TestCase):
    def test_contextualize_messages_adds_request_context(self):
        actual = contextualize_messages(
            [{"level": "warning", "code": "warning_code", "message": "warning"}],
            "./evidence.json",
            "./test.py",
        )

        self.assertEqual(actual[0]["evidence_file"], "./evidence.json")
        self.assertEqual(actual[0]["test_file"], "./test.py")
