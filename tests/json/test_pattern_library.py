import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestPatternLibraryFixtures(unittest.TestCase):
    def setUp(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.main_py = repo_root / "main.py"
        self.evidence_dir = Path(__file__).resolve().parent / "evidence"
        self.test_dir = Path(__file__).resolve().parent / "test_of_detail"

    def _run_fixture(self, evidence_name, test_name, evaluations):
        result = subprocess.run(
            [
                sys.executable,
                str(self.main_py),
                "--evidence",
                str(self.evidence_dir / evidence_name),
                "--invoke",
                json.dumps(
                    {
                        "test": str(self.test_dir / test_name),
                        "evaluations": evaluations,
                    }
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_coverage_minimum_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_component_coverage_minimum.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 90},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("90.0", output_json["results"][0]["result"]["reason"])

    def test_coverage_range_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_component_coverage_range.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 80, "maximum": 84},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("80.0% to 84.0%", output_json["results"][0]["result"]["reason"])

    def test_feature_flag_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_feature_flag_enabled.py",
            [
                {
                    "subject": {"name": "feature_enabled", "data_type": "boolean"},
                    "criteria": {"equals": False},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value False", output_json["results"][0]["result"]["reason"])

    def test_allowed_values_fixture_uses_allowed_values_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_release_status_allowed_values.py",
            [
                {
                    "subject": {"name": "release_status", "data_type": "text"},
                    "criteria": {"allowed_values": ["rejected", "pending"]},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed value set", output_json["results"][0]["result"]["reason"])

    def test_required_fixture_uses_required_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_service_owner_required.py",
            [
                {
                    "subject": {"name": "service_owner", "data_type": "text"},
                    "criteria": {"required": False},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "error")
        self.assertIn("required to be true", output_json["results"][0]["result"]["reason"])

    def test_required_fixture_returns_inconclusive_when_fact_missing(self):
        output_json = self._run_fixture(
            "component_assurance_missing_owner.json",
            "verify_service_owner_required.py",
            [
                {
                    "subject": {"name": "service_owner", "data_type": "text"},
                    "criteria": {"required": True},
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )

    def test_disallowed_values_fixture_uses_disallowed_values_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_release_status_disallowed_values.py",
            [
                {
                    "subject": {"name": "release_status", "data_type": "text"},
                    "criteria": {"disallowed_values": ["approved", "rejected"]},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "disallowed value set", output_json["results"][0]["result"]["reason"]
        )

    def test_object_equals_fixture_uses_object_input(self):
        output_json = self._run_fixture(
            "access_grant_state.json",
            "verify_approver_profile_equals.py",
            [
                {
                    "subject": {"name": "approver_profile", "data_type": "object"},
                    "criteria": {
                        "equals": {
                            "id": "manager-123",
                            "department": "finance",
                        }
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected object", output_json["results"][0]["result"]["reason"])

    def test_array_equals_fixture_uses_array_input(self):
        output_json = self._run_fixture(
            "access_grant_state.json",
            "verify_reviewer_roles_equals.py",
            [
                {
                    "subject": {"name": "reviewer_roles", "data_type": "array"},
                    "criteria": {"equals": ["security", "manager"]},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected array", output_json["results"][0]["result"]["reason"])

    def test_null_equals_fixture_uses_null_input(self):
        output_json = self._run_fixture(
            "access_grant_state.json",
            "verify_revocation_reason_null.py",
            [
                {
                    "subject": {"name": "revocation_reason", "data_type": "null"},
                    "criteria": {"equals": None},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "true")
        self.assertIn("explicitly null", output_json["results"][0]["result"]["reason"])

    def test_datetime_minimum_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "access_review.json",
            "verify_last_review_timestamp_minimum.py",
            [
                {
                    "subject": {
                        "name": "last_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-20T00:00:00Z"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "older than the required minimum datetime",
            output_json["results"][0]["result"]["reason"],
        )

    def test_datetime_range_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "access_review.json",
            "verify_last_review_timestamp_range.py",
            [
                {
                    "subject": {
                        "name": "last_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {
                        "minimum": "2026-06-01T00:00:00Z",
                        "maximum": "2026-06-10T00:00:00Z",
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("outside the allowed datetime range", output_json["results"][0]["result"]["reason"])

    def test_integer_range_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_build_age_days_range.py",
            [
                {
                    "subject": {"name": "build_age_days", "data_type": "integer"},
                    "criteria": {"minimum": 0, "maximum": 10},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("0 to 10", output_json["results"][0]["result"]["reason"])

    def test_date_range_fixture_uses_date_range_input(self):
        output_json = self._run_fixture(
            "operations_timing.json",
            "verify_review_date_range.py",
            [
                {
                    "subject": {"name": "review_date", "data_type": "date"},
                    "criteria": {
                        "minimum": "2026-06-16",
                        "maximum": "2026-06-30",
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("2026-06-16 to 2026-06-30", output_json["results"][0]["result"]["reason"])

    def test_date_range_fixture_returns_inconclusive_for_invalid_date_fact(self):
        output_json = self._run_fixture(
            "operations_timing_invalid_review_date.json",
            "verify_review_date_range.py",
            [
                {
                    "subject": {"name": "review_date", "data_type": "date"},
                    "criteria": {
                        "minimum": "2026-06-01",
                        "maximum": "2026-06-30",
                    },
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["status"], "invalid"
        )
        self.assertIn(
            "could not be established",
            output_json["results"][0]["result"]["reason"],
        )

    def test_date_range_fixture_returns_error_for_invalid_date_criteria(self):
        output_json = self._run_fixture(
            "operations_timing.json",
            "verify_review_date_range.py",
            [
                {
                    "subject": {"name": "review_date", "data_type": "date"},
                    "criteria": {
                        "minimum": "not-a-date",
                        "maximum": "2026-06-30",
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "error")
        self.assertIn("ISO-8601 dates", output_json["results"][0]["result"]["reason"])

    def test_duration_range_fixture_uses_duration_range_input(self):
        output_json = self._run_fixture(
            "operations_timing.json",
            "verify_restore_duration_range.py",
            [
                {
                    "subject": {"name": "restore_duration", "data_type": "duration"},
                    "criteria": {
                        "minimum": "PT10M",
                        "maximum": "PT30M",
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("outside the allowed duration range", output_json["results"][0]["result"]["reason"])

    def test_duration_range_fixture_returns_inconclusive_for_invalid_duration_fact(self):
        output_json = self._run_fixture(
            "operations_timing_invalid_restore_duration.json",
            "verify_restore_duration_range.py",
            [
                {
                    "subject": {"name": "restore_duration", "data_type": "duration"},
                    "criteria": {
                        "minimum": "PT10M",
                        "maximum": "PT60M",
                    },
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["status"], "invalid"
        )
        self.assertIn(
            "could not be established",
            output_json["results"][0]["result"]["reason"],
        )

    def test_duration_range_fixture_returns_error_for_invalid_duration_criteria(self):
        output_json = self._run_fixture(
            "operations_timing.json",
            "verify_restore_duration_range.py",
            [
                {
                    "subject": {"name": "restore_duration", "data_type": "duration"},
                    "criteria": {
                        "minimum": "ten minutes",
                        "maximum": "PT60M",
                    },
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "error")
        self.assertIn(
            "supported ISO-8601 durations",
            output_json["results"][0]["result"]["reason"],
        )

    def test_dual_threshold_fixture_uses_both_inputs(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_dual_coverage_thresholds.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 80},
                },
                {
                    "subject": {"name": "branch_coverage", "data_type": "number"},
                    "criteria": {"minimum": 98},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("branch_coverage is below 98.0%", output_json["results"][0]["result"]["reason"])

    def test_dual_threshold_fail_fast_fixture_returns_first_missing_fact_only(self):
        output_json = self._run_fixture(
            "component_assurance_missing_branch.json",
            "verify_dual_coverage_fail_fast.py",
            [
                {
                    "subject": {"name": "coverage", "data_type": "number"},
                    "criteria": {"minimum": 80},
                },
                {
                    "subject": {"name": "branch_coverage", "data_type": "number"},
                    "criteria": {"minimum": 95},
                },
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(len(output_json["results"][0]["result"]["facts"]), 1)
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["name"],
            "branch_coverage",
        )

    def test_derived_coverage_gap_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "component_assurance.json",
            "verify_coverage_gap_maximum.py",
            [
                {
                    "subject": {"name": "coverage_gap", "data_type": "number"},
                    "criteria": {"maximum": 10},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "allowed maximum of 10.0",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][2]["name"], "coverage_gap"
        )

    def test_derived_coverage_gap_fixture_returns_inconclusive_when_prerequisite_missing(self):
        output_json = self._run_fixture(
            "component_assurance_missing_branch.json",
            "verify_coverage_gap_maximum.py",
            [
                {
                    "subject": {"name": "coverage_gap", "data_type": "number"},
                    "criteria": {"maximum": 20},
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][1]["name"],
            "branch_coverage",
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][2]["name"], "coverage_gap"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][2]["status"], "not_found"
        )
