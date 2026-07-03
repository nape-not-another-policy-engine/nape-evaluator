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

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
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

    def test_privileged_access_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "privileged_access_grant.json",
            "verify_privileged_access_status_approved.py",
            [
                {
                    "subject": {
                        "name": "access_request_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "rejected"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("rejected", output_json["results"][0]["result"]["reason"])

    def test_privileged_access_approver_required_returns_inconclusive_when_missing(self):
        output_json = self._run_fixture(
            "privileged_access_grant_missing_approver.json",
            "verify_privileged_access_approver_required.py",
            [
                {
                    "subject": {
                        "name": "approver_identifier",
                        "data_type": "text",
                    },
                    "criteria": {"required": True},
                }
            ],
        )

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
        self.assertEqual(
            output_json["results"][0]["result"]["facts"][0]["status"], "not_found"
        )

    def test_privileged_access_review_recent_uses_minimum_input(self):
        output_json = self._run_fixture(
            "privileged_access_grant_stale_review.json",
            "verify_privileged_access_review_recent.py",
            [
                {
                    "subject": {
                        "name": "last_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("older than the required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_privileged_access_core_controls_combines_three_inputs(self):
        output_json = self._run_fixture(
            "privileged_access_grant_stale_review.json",
            "verify_privileged_access_core_controls.py",
            [
                {
                    "subject": {
                        "name": "access_request_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
                {
                    "subject": {
                        "name": "approver_identifier",
                        "data_type": "text",
                    },
                    "criteria": {"required": True},
                },
                {
                    "subject": {
                        "name": "last_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("older than the required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_restore_drill_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "utility_restore_drill_success.json",
            "verify_restore_drill_status_successful.py",
            [
                {
                    "subject": {
                        "name": "restore_drill_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "failed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("failed", output_json["results"][0]["result"]["reason"])

    def test_restore_drill_duration_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "utility_restore_drill_over_duration.json",
            "verify_restore_drill_duration_within_threshold.py",
            [
                {
                    "subject": {
                        "name": "restore_drill_duration",
                        "data_type": "duration",
                    },
                    "criteria": {"maximum": "PT1H"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("exceeds the allowed maximum duration", output_json["results"][0]["result"]["reason"])

    def test_restore_drill_recent_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "utility_restore_drill_stale.json",
            "verify_restore_drill_recent.py",
            [
                {
                    "subject": {
                        "name": "restore_drill_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("older than the required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_restore_drill_core_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "utility_restore_drill_over_duration.json",
            "verify_restore_drill_core_readiness.py",
            [
                {
                    "subject": {
                        "name": "restore_drill_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "successful"},
                },
                {
                    "subject": {
                        "name": "restore_drill_duration",
                        "data_type": "duration",
                    },
                    "criteria": {"maximum": "PT1H"},
                },
                {
                    "subject": {
                        "name": "restore_drill_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("exceeds the allowed maximum duration", output_json["results"][0]["result"]["reason"])

    def test_transport_inspection_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "transport_inspection_incomplete.json",
            "verify_transport_inspection_status_completed.py",
            [
                {
                    "subject": {
                        "name": "pre_trip_inspection_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("completed", output_json["results"][0]["result"]["reason"])

    def test_transport_inspection_recent_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "transport_inspection_stale.json",
            "verify_transport_inspection_recent.py",
            [
                {
                    "subject": {
                        "name": "inspection_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("older than the required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_transport_inspection_readiness_combines_two_inputs(self):
        output_json = self._run_fixture(
            "transport_inspection_stale.json",
            "verify_transport_inspection_readiness.py",
            [
                {
                    "subject": {
                        "name": "pre_trip_inspection_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                },
                {
                    "subject": {
                        "name": "inspection_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("older than the required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_manufacturing_maintenance_release_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "manufacturing_line_restart_ready.json",
            "verify_manufacturing_maintenance_release_approved.py",
            [
                {
                    "subject": {
                        "name": "maintenance_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "blocked"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("blocked", output_json["results"][0]["result"]["reason"])

    def test_manufacturing_work_order_fixture_uses_boolean_input(self):
        output_json = self._run_fixture(
            "manufacturing_line_restart_incomplete_work_order.json",
            "verify_manufacturing_work_order_complete.py",
            [
                {
                    "subject": {
                        "name": "work_order_complete",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("not complete", output_json["results"][0]["result"]["reason"])

    def test_manufacturing_restart_authorization_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "manufacturing_line_restart_blocked.json",
            "verify_manufacturing_restart_authorization_approved.py",
            [
                {
                    "subject": {
                        "name": "restart_authorization_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_manufacturing_line_restart_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "manufacturing_line_restart_blocked.json",
            "verify_manufacturing_line_restart_readiness.py",
            [
                {
                    "subject": {
                        "name": "maintenance_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
                {
                    "subject": {
                        "name": "work_order_complete",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "restart_authorization_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("restart_authorization_status", output_json["results"][0]["result"]["reason"])

    def test_payment_transaction_approval_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "payment_settlement_blocked.json",
            "verify_payment_transaction_approval_status.py",
            [
                {
                    "subject": {
                        "name": "transaction_approval_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_payment_settlement_difference_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "payment_settlement_over_tolerance.json",
            "verify_payment_settlement_difference_within_tolerance.py",
            [
                {
                    "subject": {
                        "name": "settlement_difference_amount",
                        "data_type": "number",
                    },
                    "criteria": {"maximum": 1},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed maximum of 1.0", output_json["results"][0]["result"]["reason"])

    def test_payment_reconciliation_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "payment_settlement_blocked.json",
            "verify_payment_reconciliation_status_completed.py",
            [
                {
                    "subject": {
                        "name": "reconciliation_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("completed", output_json["results"][0]["result"]["reason"])

    def test_payment_settlement_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "payment_settlement_over_tolerance.json",
            "verify_payment_settlement_readiness.py",
            [
                {
                    "subject": {
                        "name": "transaction_approval_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
                {
                    "subject": {
                        "name": "reconciliation_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                },
                {
                    "subject": {
                        "name": "settlement_difference_amount",
                        "data_type": "number",
                    },
                    "criteria": {"maximum": 1},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "settlement_difference_amount",
            output_json["results"][0]["result"]["reason"],
        )

    def test_medical_device_release_review_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "medical_device_release_blocked.json",
            "verify_medical_device_release_review_approved.py",
            [
                {
                    "subject": {
                        "name": "release_review_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_medical_device_sbom_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "medical_device_release_ready.json",
            "verify_medical_device_sbom_present.py",
            [
                {
                    "subject": {
                        "name": "sbom_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": False},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value False", output_json["results"][0]["result"]["reason"])

    def test_medical_device_critical_vulnerability_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "medical_device_release_blocked.json",
            "verify_medical_device_critical_vulnerability_count_maximum.py",
            [
                {
                    "subject": {
                        "name": "critical_vulnerability_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed maximum of 0", output_json["results"][0]["result"]["reason"])

    def test_medical_device_release_packet_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "medical_device_release_blocked.json",
            "verify_medical_device_release_packet_readiness.py",
            [
                {
                    "subject": {
                        "name": "release_review_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
                {
                    "subject": {
                        "name": "sbom_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "critical_vulnerability_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "release_review_status",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "critical_vulnerability_count",
            output_json["results"][0]["result"]["reason"],
        )

    def test_quality_batch_release_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "quality_batch_release_open_deviation.json",
            "verify_quality_batch_release_status_released.py",
            [
                {
                    "subject": {
                        "name": "batch_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "released"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("released", output_json["results"][0]["result"]["reason"])

    def test_quality_reviewer_present_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "quality_batch_release_ready.json",
            "verify_quality_reviewer_present.py",
            [
                {
                    "subject": {
                        "name": "quality_reviewer_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": False},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value False", output_json["results"][0]["result"]["reason"])

    def test_quality_deviation_closed_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "quality_batch_release_open_deviation.json",
            "verify_quality_deviation_closed.py",
            [
                {
                    "subject": {
                        "name": "deviation_closed",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "expected value True",
            output_json["results"][0]["result"]["reason"],
        )

    def test_quality_batch_release_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "quality_batch_release_open_deviation.json",
            "verify_quality_batch_release_readiness.py",
            [
                {
                    "subject": {
                        "name": "batch_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "released"},
                },
                {
                    "subject": {
                        "name": "quality_reviewer_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "deviation_closed",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "batch_release_status",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "deviation_closed",
            output_json["results"][0]["result"]["reason"],
        )

    def test_cold_chain_temperature_excursion_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "cold_chain_exception_open.json",
            "verify_cold_chain_temperature_excursion_count_maximum.py",
            [
                {
                    "subject": {
                        "name": "temperature_excursion_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed maximum of 0", output_json["results"][0]["result"]["reason"])

    def test_cold_chain_custody_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "cold_chain_exception_incomplete_custody.json",
            "verify_cold_chain_chain_of_custody_complete.py",
            [
                {
                    "subject": {
                        "name": "chain_of_custody_complete",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_cold_chain_exception_closed_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "cold_chain_exception_open.json",
            "verify_cold_chain_exception_closed.py",
            [
                {
                    "subject": {
                        "name": "exception_closed",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_cold_chain_exception_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "cold_chain_exception_open.json",
            "verify_cold_chain_exception_readiness.py",
            [
                {
                    "subject": {
                        "name": "temperature_excursion_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                },
                {
                    "subject": {
                        "name": "chain_of_custody_complete",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "exception_closed",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "temperature_excursion_count",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "exception_closed",
            output_json["results"][0]["result"]["reason"],
        )

    def test_system_interconnection_approval_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "system_event_confirmation_missing_approval.json",
            "verify_system_interconnection_approval_present.py",
            [
                {
                    "subject": {
                        "name": "interconnection_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_system_event_confirmation_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "system_event_confirmation_mismatch.json",
            "verify_system_event_confirmation_status_confirmed.py",
            [
                {
                    "subject": {
                        "name": "event_confirmation_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "confirmed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("confirmed", output_json["results"][0]["result"]["reason"])

    def test_system_cross_state_match_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "system_event_confirmation_mismatch.json",
            "verify_system_cross_state_match.py",
            [
                {
                    "subject": {
                        "name": "cross_system_state_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_system_of_systems_event_confirmation_combines_three_inputs(self):
        output_json = self._run_fixture(
            "system_event_confirmation_mismatch.json",
            "verify_system_of_systems_event_confirmation.py",
            [
                {
                    "subject": {
                        "name": "interconnection_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "event_confirmation_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "confirmed"},
                },
                {
                    "subject": {
                        "name": "cross_system_state_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "event_confirmation_status",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "cross_system_state_match",
            output_json["results"][0]["result"]["reason"],
        )

    def test_it_ot_remote_access_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "it_ot_boundary_remote_access_enabled.json",
            "verify_it_ot_remote_access_disabled.py",
            [
                {
                    "subject": {
                        "name": "remote_access_enabled",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": False},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value False", output_json["results"][0]["result"]["reason"])

    def test_it_ot_exposed_controller_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "it_ot_boundary_exposed.json",
            "verify_it_ot_internet_exposed_controller_count_maximum.py",
            [
                {
                    "subject": {
                        "name": "internet_exposed_controller_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed maximum of 0", output_json["results"][0]["result"]["reason"])

    def test_it_ot_boundary_control_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "it_ot_boundary_exposed.json",
            "verify_it_ot_boundary_control_segmented.py",
            [
                {
                    "subject": {
                        "name": "boundary_control_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "segmented"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("segmented", output_json["results"][0]["result"]["reason"])

    def test_it_ot_boundary_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "it_ot_boundary_exposed.json",
            "verify_it_ot_boundary_readiness.py",
            [
                {
                    "subject": {
                        "name": "remote_access_enabled",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": False},
                },
                {
                    "subject": {
                        "name": "internet_exposed_controller_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                },
                {
                    "subject": {
                        "name": "boundary_control_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "segmented"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "internet_exposed_controller_count",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "boundary_control_status",
            output_json["results"][0]["result"]["reason"],
        )

    def test_application_mfa_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "application_release_mfa_disabled.json",
            "verify_application_mfa_required.py",
            [
                {
                    "subject": {
                        "name": "mfa_required",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_application_critical_vulnerability_fixture_uses_maximum_input(self):
        output_json = self._run_fixture(
            "application_release_blocked.json",
            "verify_application_critical_vulnerability_count_maximum.py",
            [
                {
                    "subject": {
                        "name": "critical_vulnerability_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("allowed maximum of 0", output_json["results"][0]["result"]["reason"])

    def test_application_deployment_approval_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "application_release_blocked.json",
            "verify_application_deployment_approval_present.py",
            [
                {
                    "subject": {
                        "name": "deployment_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_application_release_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "application_release_blocked.json",
            "verify_application_release_readiness.py",
            [
                {
                    "subject": {
                        "name": "mfa_required",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "critical_vulnerability_count",
                        "data_type": "integer",
                    },
                    "criteria": {"maximum": 0},
                },
                {
                    "subject": {
                        "name": "deployment_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "critical_vulnerability_count",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "deployment_approval_present",
            output_json["results"][0]["result"]["reason"],
        )

    def test_mission_access_status_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "mission_access_review_ready.json",
            "verify_mission_access_status_authorized.py",
            [
                {
                    "subject": {
                        "name": "mission_access_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "revoked"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("revoked", output_json["results"][0]["result"]["reason"])

    def test_mission_access_approval_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "mission_access_review_missing_approval.json",
            "verify_mission_access_approval_present.py",
            [
                {
                    "subject": {
                        "name": "mission_access_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_mission_access_review_recent_fixture_uses_minimum_input(self):
        output_json = self._run_fixture(
            "mission_access_review_stale.json",
            "verify_mission_access_review_recent.py",
            [
                {
                    "subject": {
                        "name": "mission_access_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("required minimum datetime", output_json["results"][0]["result"]["reason"])

    def test_mission_access_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "mission_access_review_stale.json",
            "verify_mission_access_readiness.py",
            [
                {
                    "subject": {
                        "name": "mission_access_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "authorized"},
                },
                {
                    "subject": {
                        "name": "mission_access_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "mission_access_review_timestamp",
                        "data_type": "datetime",
                    },
                    "criteria": {"minimum": "2026-06-01T00:00:00Z"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "mission_access_review_timestamp",
            output_json["results"][0]["result"]["reason"],
        )

    def test_fleet_trip_record_present_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "fleet_telematics_missing_trip.json",
            "verify_fleet_trip_record_present.py",
            [
                {
                    "subject": {
                        "name": "trip_record_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_fleet_telematics_vehicle_match_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "fleet_telematics_mismatch.json",
            "verify_fleet_telematics_vehicle_match.py",
            [
                {
                    "subject": {
                        "name": "telematics_vehicle_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_fleet_telematics_state_match_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "fleet_telematics_mismatch.json",
            "verify_fleet_telematics_state_match.py",
            [
                {
                    "subject": {
                        "name": "telematics_state_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_fleet_telematics_reconciliation_combines_three_inputs(self):
        output_json = self._run_fixture(
            "fleet_telematics_mismatch.json",
            "verify_fleet_telematics_reconciliation.py",
            [
                {
                    "subject": {
                        "name": "trip_record_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "telematics_vehicle_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "telematics_state_match",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "telematics_vehicle_match",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "telematics_state_match",
            output_json["results"][0]["result"]["reason"],
        )

    def test_return_to_service_maintenance_release_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "return_to_service_blocked.json",
            "verify_return_to_service_maintenance_release_approved.py",
            [
                {
                    "subject": {
                        "name": "maintenance_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", output_json["results"][0]["result"]["reason"])

    def test_return_to_service_hazard_closure_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "return_to_service_open_hazard.json",
            "verify_return_to_service_hazard_closure_closed.py",
            [
                {
                    "subject": {
                        "name": "hazard_closure_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "closed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("closed", output_json["results"][0]["result"]["reason"])

    def test_return_to_service_calibration_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "return_to_service_blocked.json",
            "verify_return_to_service_calibration_current.py",
            [
                {
                    "subject": {
                        "name": "calibration_current",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_return_to_service_readiness_combines_three_inputs(self):
        output_json = self._run_fixture(
            "return_to_service_blocked.json",
            "verify_return_to_service_readiness.py",
            [
                {
                    "subject": {
                        "name": "maintenance_release_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "approved"},
                },
                {
                    "subject": {
                        "name": "hazard_closure_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "closed"},
                },
                {
                    "subject": {
                        "name": "calibration_current",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "maintenance_release_status",
            output_json["results"][0]["result"]["reason"],
        )
        self.assertIn(
            "calibration_current",
            output_json["results"][0]["result"]["reason"],
        )

    def test_patient_data_export_ticket_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "patient_data_export_missing_approval.json",
            "verify_patient_data_export_ticket_present.py",
            [
                {
                    "subject": {
                        "name": "data_export_ticket_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "true")
        self.assertIn(
            "matches the expected value",
            output_json["results"][0]["result"]["reason"],
        )

    def test_patient_data_export_approval_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "patient_data_export_missing_approval.json",
            "verify_patient_data_export_approval_present.py",
            [
                {
                    "subject": {
                        "name": "data_export_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("expected value True", output_json["results"][0]["result"]["reason"])

    def test_patient_data_retention_fixture_uses_equals_input(self):
        output_json = self._run_fixture(
            "patient_data_export_retention_pending.json",
            "verify_patient_data_retention_execution_completed.py",
            [
                {
                    "subject": {
                        "name": "retention_execution_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                }
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn("completed", output_json["results"][0]["result"]["reason"])

    def test_patient_data_export_governance_combines_three_inputs(self):
        output_json = self._run_fixture(
            "patient_data_export_missing_approval.json",
            "verify_patient_data_export_governance.py",
            [
                {
                    "subject": {
                        "name": "data_export_ticket_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "data_export_approval_present",
                        "data_type": "boolean",
                    },
                    "criteria": {"equals": True},
                },
                {
                    "subject": {
                        "name": "retention_execution_status",
                        "data_type": "text",
                    },
                    "criteria": {"equals": "completed"},
                },
            ],
        )

        self.assertEqual(output_json["results"][0]["result"]["conclusion"], "false")
        self.assertIn(
            "data_export_approval_present",
            output_json["results"][0]["result"]["reason"],
        )

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

    def test_date_range_fixture_returns_inconclusive_for_invalid_date_criteria(self):
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

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
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

    def test_duration_range_fixture_returns_inconclusive_for_invalid_duration_criteria(self):
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

        self.assertEqual(
            output_json["results"][0]["result"]["conclusion"], "inconclusive"
        )
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
