import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from nape_evaluator.application.driver.evidence_gateway import FileSystemEvidenceGateway
from nape_evaluator.domain.gateways import EvidenceLoadFailure


class TestPdfEvidenceLoading(unittest.TestCase):
    def setUp(self):
        self.gateway = FileSystemEvidenceGateway()

    def test_load_pdf_evidence_input_returns_text_lines(self):
        class FakePage:
            def extract_text(self):
                return "line one\nline two"

        class FakeReader:
            def __init__(self, file_obj):
                self.pages = [FakePage()]

        fake_pypdf2 = types.SimpleNamespace(PdfReader=FakeReader)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n")
            previous_pdf = sys.modules.get("PyPDF2")
            sys.modules["PyPDF2"] = fake_pypdf2
            try:
                evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_pdf is None:
                    del sys.modules["PyPDF2"]
                else:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(evidence, ["line one", "line two"])
        self.assertEqual(metadata["evidence_type"], "pdf")
        self.assertEqual(messages, [])

    def test_load_pdf_without_dependency_raises_evidence_load_failure(self):
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "PyPDF2":
                raise ImportError("missing pypdf2")
            return original_import(name, globals, locals, fromlist, level)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n")
            previous_pdf = sys.modules.pop("PyPDF2", None)
            try:
                with patch("builtins.__import__", side_effect=fake_import):
                    with self.assertRaises(EvidenceLoadFailure) as context:
                        self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_pdf is not None:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(context.exception.messages[-1]["code"], "evidence_load_error")
        self.assertIn("PyPDF2", context.exception.messages[-1]["message"])

    def test_load_pdf_with_multiple_pages_concatenates_lines(self):
        class FakePage:
            def __init__(self, text):
                self.text = text

            def extract_text(self):
                return self.text

        class FakeReader:
            def __init__(self, file_obj):
                self.pages = [FakePage("line one"), FakePage("line two\nline three")]

        fake_pypdf2 = types.SimpleNamespace(PdfReader=FakeReader)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n")
            previous_pdf = sys.modules.get("PyPDF2")
            sys.modules["PyPDF2"] = fake_pypdf2
            try:
                evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_pdf is None:
                    del sys.modules["PyPDF2"]
                else:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(evidence, ["line oneline two", "line three"])
        self.assertEqual(metadata["evidence_type"], "pdf")
        self.assertEqual(messages, [])

    def test_load_pdf_ignores_none_page_text(self):
        class FakePage:
            def __init__(self, text):
                self.text = text

            def extract_text(self):
                return self.text

        class FakeReader:
            def __init__(self, file_obj):
                self.pages = [FakePage(None), FakePage("line two")]

        fake_pypdf2 = types.SimpleNamespace(PdfReader=FakeReader)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n")
            previous_pdf = sys.modules.get("PyPDF2")
            sys.modules["PyPDF2"] = fake_pypdf2
            try:
                evidence, metadata, messages = self.gateway.load_evidence_input(str(evidence_path))
            finally:
                if previous_pdf is None:
                    del sys.modules["PyPDF2"]
                else:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(evidence, ["line two"])
        self.assertEqual(metadata["evidence_type"], "pdf")
        self.assertEqual(messages, [])
