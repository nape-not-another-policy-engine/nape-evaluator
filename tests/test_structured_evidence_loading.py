import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from nape_evaluator.application.driver.evidence_gateway import FileSystemEvidenceGateway
from nape_evaluator.domain.gateways import EvidenceLoadFailure


class TestStructuredEvidenceLoading(unittest.TestCase):
    def setUp(self):
        self.gateway = FileSystemEvidenceGateway()

    def test_load_json_evidence_input_returns_object(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            evidence_path.write_text('{"status":"complete"}', encoding="utf-8")
            evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(evidence["status"], "complete")
        self.assertEqual(metadata["evidence_type"], "json")
        self.assertEqual(messages, [])

    def test_invalid_json_raises_evidence_load_failure_with_error_message(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "invalid.json"
            evidence_path.write_text("{invalid json", encoding="utf-8")

            with self.assertRaises(EvidenceLoadFailure) as context:
                self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(context.exception.messages[-1]["code"], "evidence_load_error")
        self.assertEqual(context.exception.messages[-1]["evidence_file"], str(evidence_path))

    def test_load_xml_evidence_input_returns_root_element(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.xml"
            evidence_path.write_text("<author><status>complete</status></author>", encoding="utf-8")
            evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(evidence.tag, "author")
        self.assertEqual(metadata["evidence_type"], "xml")
        self.assertEqual(messages, [])

    def test_load_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.gateway.load_evidence_input("./does-not-exist.json")

    def test_load_yaml_evidence_input_returns_object(self):
        fake_yaml = types.SimpleNamespace(
            safe_load=lambda stream: {"status": "complete", "raw": stream.read()}
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.yaml"
            evidence_path.write_text("status: complete\n", encoding="utf-8")
            previous_yaml = sys.modules.get("yaml")
            sys.modules["yaml"] = fake_yaml
            try:
                evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_yaml is None:
                    del sys.modules["yaml"]
                else:
                    sys.modules["yaml"] = previous_yaml

        self.assertEqual(evidence["status"], "complete")
        self.assertEqual(metadata["evidence_type"], "yaml")
        self.assertEqual(messages, [])

    def test_load_yml_evidence_input_uses_yaml_loader(self):
        fake_yaml = types.SimpleNamespace(
            safe_load=lambda stream: {"status": "complete", "raw": stream.read()}
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.yml"
            evidence_path.write_text("status: complete\n", encoding="utf-8")
            previous_yaml = sys.modules.get("yaml")
            sys.modules["yaml"] = fake_yaml
            try:
                evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_yaml is None:
                    del sys.modules["yaml"]
                else:
                    sys.modules["yaml"] = previous_yaml

        self.assertEqual(evidence["status"], "complete")
        self.assertEqual(metadata["evidence_type"], "yaml")
        self.assertEqual(messages, [])

    def test_load_yaml_without_dependency_raises_evidence_load_failure(self):
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "yaml":
                raise ImportError("missing yaml")
            return original_import(name, globals, locals, fromlist, level)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.yaml"
            evidence_path.write_text("status: complete\n", encoding="utf-8")
            previous_yaml = sys.modules.pop("yaml", None)
            try:
                with patch("builtins.__import__", side_effect=fake_import):
                    with self.assertRaises(EvidenceLoadFailure) as context:
                        self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_yaml is not None:
                    sys.modules["yaml"] = previous_yaml

        self.assertEqual(context.exception.messages[-1]["code"], "evidence_load_error")
        self.assertIn("PyYAML", context.exception.messages[-1]["message"])
