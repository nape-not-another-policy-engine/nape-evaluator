import unittest
from pathlib import Path

from nape_evaluator.application.driver.evidence_gateway import (
    DEFAULT_EVIDENCE_LOADER,
    EVIDENCE_LOADERS,
    FileSystemEvidenceGateway,
)


class TestEvidenceGatewayRouting(unittest.TestCase):
    def setUp(self):
        self.gateway = FileSystemEvidenceGateway()

    def test_resolve_text_loader_for_missing_extension(self):
        strategy = self.gateway.resolve_evidence_loader(Path("evidence"))
        self.assertEqual(strategy.evidence_type, "text")
        self.assertEqual(strategy, DEFAULT_EVIDENCE_LOADER)

    def test_resolve_text_loader_for_txt_file(self):
        strategy = self.gateway.resolve_evidence_loader(Path("evidence.txt"))
        self.assertEqual(strategy.evidence_type, "text")

    def test_resolve_json_loader(self):
        strategy = self.gateway.resolve_evidence_loader(Path("evidence.json"))
        self.assertEqual(strategy, EVIDENCE_LOADERS[".json"])

    def test_resolve_unknown_extension_defaults_to_text(self):
        strategy = self.gateway.resolve_evidence_loader(Path("evidence.unknown"))
        self.assertEqual(strategy.evidence_type, "text")
        self.assertEqual(strategy, DEFAULT_EVIDENCE_LOADER)

    def test_metadata_for_missing_extension_uses_text(self):
        metadata = self.gateway.build_evidence_metadata(
            self.gateway.resolve_evidence_loader(Path("evidence"))
        )
        self.assertEqual(metadata["evidence_type"], "text")
        self.assertEqual(metadata["schema_version"], "2")

    def test_metadata_for_json_uses_json(self):
        metadata = self.gateway.build_evidence_metadata(
            self.gateway.resolve_evidence_loader(Path("evidence.json"))
        )
        self.assertEqual(metadata["evidence_type"], "json")
        self.assertEqual(metadata["schema_version"], "2")
