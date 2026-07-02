import unittest

from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    RequestValidationError,
)


class TestRequestBuilder(unittest.TestCase):
    def test_builder_creates_verified_request(self):
        request = (
            EvaluateEvidenceRequest.builder()
            .evidence_path("./evidence.json")
            .raw_tests(
                [
                    {
                        "test": "./coverage.py",
                        "evaluations": [
                            {
                                "subject": {
                                    "name": "coverage",
                                    "data_type": "number",
                                },
                                "criteria": {"minimum": 80},
                            }
                        ],
                    }
                ]
            )
            .try_build()
        )

        self.assertEqual(request.evidence_path, "./evidence.json")
        self.assertEqual(len(request.test_invocations), 1)
        self.assertEqual(request.test_invocations[0].test_path, "./coverage.py")

    def test_builder_rejects_invalid_subject_name(self):
        with self.assertRaises(RequestValidationError):
            (
                EvaluateEvidenceRequest.builder()
                .evidence_path("./evidence.json")
                .raw_tests(
                    [
                        {
                            "test": "./coverage.py",
                            "evaluations": [
                                {
                                    "subject": {
                                        "name": "Coverage Rate",
                                        "data_type": "number",
                                    },
                                    "criteria": {"minimum": 80},
                                }
                            ],
                        }
                    ]
                )
                .try_build()
            )

    def test_builder_rejects_invalid_subject_data_type(self):
        with self.assertRaises(RequestValidationError):
            (
                EvaluateEvidenceRequest.builder()
                .evidence_path("./evidence.json")
                .raw_tests(
                    [
                        {
                            "test": "./coverage.py",
                            "evaluations": [
                                {
                                    "subject": {
                                        "name": "coverage",
                                        "data_type": "percentage",
                                    },
                                    "criteria": {"minimum": 80},
                                }
                            ],
                        }
                    ]
                )
                .try_build()
            )

    def test_builder_rejects_invalid_criteria_key(self):
        with self.assertRaises(RequestValidationError):
            (
                EvaluateEvidenceRequest.builder()
                .evidence_path("./evidence.json")
                .raw_tests(
                    [
                        {
                            "test": "./coverage.py",
                            "evaluations": [
                                {
                                    "subject": {
                                        "name": "coverage",
                                        "data_type": "number",
                                    },
                                    "criteria": {"threshold_split": 95},
                                }
                            ],
                        }
                    ]
                )
                .try_build()
            )

    def test_builder_rejects_incompatible_criteria(self):
        with self.assertRaises(RequestValidationError):
            (
                EvaluateEvidenceRequest.builder()
                .evidence_path("./evidence.json")
                .raw_tests(
                    [
                        {
                            "test": "./coverage.py",
                            "evaluations": [
                                {
                                    "subject": {
                                        "name": "status",
                                        "data_type": "text",
                                    },
                                    "criteria": {"minimum": 80},
                                }
                            ],
                        }
                    ]
                )
                .try_build()
            )
