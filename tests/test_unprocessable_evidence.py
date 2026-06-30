import tempfile
import unittest
from pathlib import Path

from nape_evaluator.application.driver.evidence_gateway import (
    UNPROCESSABLE_EXTENSIONS,
    FileSystemEvidenceGateway,
)
from nape_evaluator.domain.gateways import EvidenceLoadFailure


class TestUnprocessableEvidence(unittest.TestCase):
    def setUp(self):
        self.gateway = FileSystemEvidenceGateway()

    def test_unprocessable_extension_set_lists_common_binary_types(self):
        self.assertIn(".png", UNPROCESSABLE_EXTENSIONS)
        self.assertIn(".zip", UNPROCESSABLE_EXTENSIONS)
        self.assertIn(".exe", UNPROCESSABLE_EXTENSIONS)

    def test_load_unprocessable_extension_raises_evidence_error_for_each_listed_extension(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            for extension in sorted(UNPROCESSABLE_EXTENSIONS):
                evidence_path = Path(tmp_dir) / f"blocked{extension}"
                evidence_path.write_bytes(b"\x00")

                with self.assertRaises(EvidenceLoadFailure) as context:
                    self.gateway.load_evidence_input(str(evidence_path))

                self.assertEqual(
                    context.exception.messages[0]["code"],
                    "unprocessable_evidence_type",
                )
                self.assertEqual(
                    context.exception.messages[0]["evidence_file"],
                    str(evidence_path),
                )
