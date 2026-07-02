import sys
import tempfile
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nape_evaluator.application.driver.evidence_gateway import FileSystemEvidenceGateway
from nape_evaluator.application.driver.test_of_detail_gateway import (
    PythonTestOfDetailGateway,
)
from nape_evaluator.domain.use_case_models import EvaluateEvidenceRequest
from nape_evaluator.domain.use_cases import evaluate_request


class _FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class _FakeReader:
    def __init__(self, handle):
        del handle
        self.pages = [_FakePage("Author: Bill Bensing\nStatus: complete\n")]


class _AmbiguousFakeReader:
    def __init__(self, handle):
        del handle
        self.pages = [_FakePage("Author: Bill Bensing\nStatus: pending\nStatus: complete\n")]


class TestPdfPatternLibraryFixtures(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "test_of_detail"

    def test_pdf_status_fixture_uses_equals_input(self):
        fake_pypdf2 = types.SimpleNamespace(PdfReader=_FakeReader)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "author_verification.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n%example\n")

            previous_pdf = sys.modules.get("PyPDF2")
            sys.modules["PyPDF2"] = fake_pypdf2
            try:
                request = (
                    EvaluateEvidenceRequest.builder()
                    .evidence_path(str(evidence_path))
                    .raw_tests(
                        [
                            {
                                "test": str(
                                    self.test_dir / "verify_author_complete.py"
                                ),
                                "evaluations": [
                                    {
                                        "subject": {
                                            "name": "status",
                                            "data_type": "text",
                                        },
                                        "criteria": {"equals": "approved"},
                                    }
                                ],
                            }
                        ]
                    )
                    .try_build()
                )

                response = evaluate_request(
                    request,
                    FileSystemEvidenceGateway(),
                    PythonTestOfDetailGateway(),
                ).to_cli_output()
            finally:
                if previous_pdf is None:
                    del sys.modules["PyPDF2"]
                else:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(response["results"][0]["result"]["conclusion"], "false")
        self.assertIn("approved", response["results"][0]["result"]["reason"])

    def test_pdf_ambiguous_status_fixture_returns_inconclusive(self):
        fake_pypdf2 = types.SimpleNamespace(PdfReader=_AmbiguousFakeReader)

        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "author_verification.pdf"
            evidence_path.write_bytes(b"%PDF-1.4\n%example\n")

            previous_pdf = sys.modules.get("PyPDF2")
            sys.modules["PyPDF2"] = fake_pypdf2
            try:
                request = (
                    EvaluateEvidenceRequest.builder()
                    .evidence_path(str(evidence_path))
                    .raw_tests(
                        [
                            {
                                "test": str(
                                    self.test_dir
                                    / "verify_author_complete_ambiguous.py"
                                ),
                                "evaluations": [
                                    {
                                        "subject": {
                                            "name": "status",
                                            "data_type": "text",
                                        },
                                        "criteria": {"equals": "complete"},
                                    }
                                ],
                            }
                        ]
                    )
                    .try_build()
                )

                response = evaluate_request(
                    request,
                    FileSystemEvidenceGateway(),
                    PythonTestOfDetailGateway(),
                ).to_cli_output()
            finally:
                if previous_pdf is None:
                    del sys.modules["PyPDF2"]
                else:
                    sys.modules["PyPDF2"] = previous_pdf

        self.assertEqual(response["results"][0]["result"]["conclusion"], "inconclusive")
        self.assertEqual(response["results"][0]["result"]["facts"][0]["status"], "invalid")
