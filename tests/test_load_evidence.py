import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import main


class TestLoadEvidence(unittest.TestCase):
    def test_load_json_returns_dict(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.json"
            evidence_path.write_text('{"status": "complete"}', encoding="utf-8")

            evidence = main.load_evidence(str(evidence_path))

        self.assertEqual(evidence, {"status": "complete"})

    def test_load_yaml_returns_dict(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.yaml"
            evidence_path.write_text("status: complete\n", encoding="utf-8")

            evidence = main.load_evidence(str(evidence_path))

        self.assertEqual(evidence, {"status": "complete"})

    def test_load_xml_returns_root_element(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.xml"
            evidence_path.write_text("<author><status>complete</status></author>", encoding="utf-8")

            evidence = main.load_evidence(str(evidence_path))

        self.assertIsInstance(evidence, ET.Element)
        self.assertEqual(evidence.tag, "author")

    def test_load_text_returns_lines(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.txt"
            evidence_path.write_text("line1\nline2\n", encoding="utf-8")

            evidence = main.load_evidence(str(evidence_path))

        self.assertEqual(evidence, ["line1\n", "line2\n"])

    def test_unknown_extension_falls_back_to_text_lines(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            evidence_path = Path(tmp_dir) / "evidence.data"
            evidence_path.write_text("line1\n", encoding="utf-8")

            evidence = main.load_evidence(str(evidence_path))

        self.assertEqual(evidence, ["line1\n"])

    def test_missing_file_raises_value_error(self):
        with self.assertRaises(ValueError):
            main.load_evidence("/definitely/missing/evidence.json")
