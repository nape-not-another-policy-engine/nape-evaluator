import tempfile
import unittest
from pathlib import Path

from nape_evaluator.application.driver.evidence_gateway import FileSystemEvidenceGateway


class TestTextEvidenceLoading(unittest.TestCase):
    def setUp(self):
        self.gateway = FileSystemEvidenceGateway()

    def test_load_text_evidence_input_returns_lines_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.txt"
            evidence_path.write_text("hello", encoding="utf-8")
            evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(evidence, ["hello"])
        self.assertEqual(metadata["evidence_type"], "text")
        self.assertEqual(messages, [])

    def test_load_missing_extension_emits_warning(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence"
            evidence_path.write_text("hello", encoding="utf-8")
            evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(evidence, ["hello"])
        self.assertEqual(metadata["evidence_type"], "text")
        self.assertEqual(messages[0]["code"], "missing_extension_text_fallback")

    def test_load_unknown_extension_emits_warning_and_treats_evidence_as_text(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.dat"
            evidence_path.write_text("hello", encoding="utf-8")
            evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))

        self.assertEqual(evidence, ["hello"])
        self.assertEqual(metadata["evidence_type"], "text")
        self.assertEqual(messages[0]["code"], "unknown_extension_text_fallback")
