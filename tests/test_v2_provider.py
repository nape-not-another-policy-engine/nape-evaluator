import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CONTRACT = "attestify.nape-evaluator.action-invocation/v2"
PROFILE = "attestify-python-test-development-v1"
PROFILE_RUNTIME_AVAILABLE = (
    sys.implementation.name == "cpython"
    and sys.version_info[:3] == (3, 11, 6)
    and sys.platform.startswith("linux")
)


class TestVersionedV2Provider(unittest.TestCase):
    def setUp(self):
        self.repo = Path(__file__).resolve().parents[1]
        self.workspace_repo = self.repo.parents[1]
        configured_executable = os.environ.get("NAPE_EVALUATOR_TEST_EXECUTABLE")
        self.command = (
            [configured_executable]
            if configured_executable
            else [sys.executable, str(self.repo / "main.py")]
        )
        self.golden = (
            self.workspace_repo
            / "2-other-workspaces"
            / "attestify-design"
            / "attestify-product-specification"
            / "05-specs"
            / "products"
            / "verification-engine"
            / "schemas"
            / "i0-i4"
            / "conformance"
            / "golden"
            / "step-4"
        )

    def _invoke(
        self,
        evidence_source,
        *,
        test_source=None,
        test_source_bytes=None,
        mutate=None,
        maximum_work=25_000_000,
        maximum_result=131_072,
    ):
        test_source = test_source or (
            self.golden
            / "source"
            / "package"
            / "a0-procedure"
            / "activity"
            / "release-readiness"
            / "database-connection"
            / "database-connection.py"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            evidence_path = root / "evidence" / "application-configuration.json"
            test_path = root / "package" / "database-connection.py"
            evidence_path.parent.mkdir(mode=0o700)
            test_path.parent.mkdir(mode=0o700)
            evidence_bytes = Path(evidence_source).read_bytes()
            test_bytes = (
                test_source_bytes
                if test_source_bytes is not None
                else Path(test_source).read_bytes()
            )
            evidence_path.write_bytes(evidence_bytes)
            test_path.write_bytes(test_bytes)
            request = {
                "contract": CONTRACT,
                "workspace_root": str(root),
                "evidence": {
                    "file": "evidence/application-configuration.json",
                    "argument_digest": "sha256:"
                    + hashlib.sha256(evidence_bytes).hexdigest(),
                    "argument_byte_count": len(evidence_bytes),
                    "media_type": "application/json",
                    "representation": "opaque",
                },
                "test": {
                    "file": "package/database-connection.py",
                    "content_digest": "sha256:"
                    + hashlib.sha256(test_bytes).hexdigest(),
                    "byte_count": len(test_bytes),
                    "runner_profile": PROFILE,
                },
                "evaluations": [],
                "metadata": {
                    "evidence_media_type": "application/json",
                    "evidence_representation": "opaque",
                    "evaluator_contract_version": "2",
                },
                "limits": {
                    "maximum_execution_work_units": maximum_work,
                    "maximum_result_bytes": maximum_result,
                },
            }
            if mutate is not None:
                mutate(request)
            completed = subprocess.run(
                [*self.command, "--request-file", "-"],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            self.assertTrue(completed.stdout.endswith("\n"))
            self.assertEqual(completed.stdout.count("\n"), 1)
            return json.loads(completed.stdout)

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_a0_true_matches_frozen_semantics(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json"
        )
        expected = json.loads(
            (
                self.golden
                / "generated"
                / "scenario"
                / "GF-01"
                / "evaluator-response.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(response, expected)

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_a0_false_matches_frozen_semantics(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "false"
            / "application-configuration.json"
        )
        expected = json.loads(
            (
                self.golden
                / "generated"
                / "scenario"
                / "GF-02"
                / "evaluator-response.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(response, expected)

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_a0_missing_fact_matches_frozen_semantics(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "missing"
            / "application-configuration.json"
        )
        expected = json.loads(
            (
                self.golden
                / "generated"
                / "scenario"
                / "GF-03"
                / "evaluator-response.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(response, expected)

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_a0_malformed_evidence_matches_frozen_semantics(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "malformed"
            / "application-configuration.json"
        )
        expected = json.loads(
            (
                self.golden
                / "generated"
                / "scenario"
                / "GF-04"
                / "evaluator-response.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(response, expected)

    def test_wrong_contract_does_not_downgrade(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            mutate=lambda request: request.__setitem__(
                "contract", "attestify.nape-evaluator.action-invocation/v3"
            ),
        )
        self.assertEqual(response["disposition"], "request-rejected")
        self.assertEqual(response["diagnostic"]["code"], "evaluator_request_invalid")

    def test_evidence_digest_mismatch_is_integrity_failure(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            mutate=lambda request: request["evidence"].__setitem__(
                "argument_digest", "sha256:" + ("0" * 64)
            ),
        )
        self.assertEqual(response["disposition"], "integrity-failed")
        self.assertEqual(
            response["diagnostic"]["code"], "evidence_argument_integrity_failed"
        )

    def test_metadata_mismatch_is_rejected(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            mutate=lambda request: request["metadata"].__setitem__(
                "evidence_media_type", "text/plain"
            ),
        )
        self.assertEqual(response["disposition"], "request-rejected")
        self.assertEqual(
            response["diagnostic"]["code"], "invalid_metadata_contract"
        )

    def test_denied_import_is_rejected_before_activation(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            test_source_bytes=(
                b"import os\n\n"
                b"def evaluate(evidence, evaluations, metadata):\n"
                b"    return {'conclusion': 'true', 'facts': [], 'reason': 'bad'}\n"
            ),
        )
        self.assertEqual(response["disposition"], "request-rejected")
        self.assertEqual(response["diagnostic"]["code"], "evaluator_request_invalid")

    def test_bare_exception_handler_cannot_catch_runner_limits(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            test_source_bytes=(
                b"def evaluate(evidence, evaluations, metadata):\n"
                b"    try:\n"
                b"        return {'conclusion': 'true', 'facts': [], 'reason': 'x'}\n"
                b"    except:\n"
                b"        return {'conclusion': 'true', 'facts': [], 'reason': 'bypass'}\n"
            ),
        )
        self.assertEqual(response["disposition"], "request-rejected")
        self.assertEqual(response["diagnostic"]["code"], "evaluator_request_invalid")

    def test_unknown_request_member_is_rejected(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            mutate=lambda request: request.__setitem__("procedure", "forbidden"),
        )
        self.assertEqual(response["disposition"], "request-rejected")
        self.assertEqual(response["diagnostic"]["code"], "evaluator_request_invalid")

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_invalid_normal_return_is_contained(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            test_source_bytes=(
                b"def evaluate(evidence, evaluations, metadata):\n"
                b"    return {'conclusion': 'true'}\n"
            ),
        )
        self.assertEqual(
            response["diagnostic"]["code"], "completed_invalid_result_contract"
        )
        self.assertEqual(response["semantic_owner"], "verification-engine")

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_valid_result_over_limit_is_contained_without_truncation(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            test_source_bytes=(
                b"def evaluate(evidence, evaluations, metadata):\n"
                b"    return {'conclusion': 'true', 'facts': [], 'reason': 'abcdefgh'}\n"
            ),
            maximum_result=1,
        )
        self.assertEqual(
            response["diagnostic"]["code"], "completed_result_limit_exceeded"
        )
        self.assertNotIn("abcdefgh", json.dumps(response))

    @unittest.skipUnless(
        PROFILE_RUNTIME_AVAILABLE, "requires the exact Linux CPython 3.11.6 profile"
    )
    def test_work_precharge_above_limit_is_contained(self):
        response = self._invoke(
            self.golden
            / "source"
            / "evidence"
            / "true"
            / "application-configuration.json",
            maximum_work=1,
        )
        self.assertEqual(response["disposition"], "occurrence-result")
        self.assertEqual(
            response["diagnostic"]["code"],
            "test_execution_work_limit_exceeded",
        )


if __name__ == "__main__":
    unittest.main()
