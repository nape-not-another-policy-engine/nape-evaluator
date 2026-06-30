from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Dict, List, Tuple
import xml.etree.ElementTree as ET

from nape_evaluator.application.io.output_contract import build_message
from nape_evaluator.domain.gateways import EvidenceLoadFailure

SCHEMA_VERSION = "2"


@dataclass(frozen=True)
class EvidenceLoaderStrategy:
    evidence_type: str
    load: Callable[[str], Any]


def _load_text(evidence_path):
    with open(evidence_path, "r", encoding="utf-8") as f:
        return f.readlines()


def _load_json(evidence_path):
    with open(evidence_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_xml(evidence_path):
    tree = ET.parse(evidence_path)
    return tree.getroot()


def _load_yaml(evidence_path):
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("YAML support requires PyYAML to be installed.") from exc

    with open(evidence_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_pdf(evidence_path):
    try:
        import PyPDF2
    except ImportError as exc:
        raise RuntimeError("PDF support requires PyPDF2 to be installed.") from exc

    with open(evidence_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.splitlines()


DEFAULT_EVIDENCE_LOADER = EvidenceLoaderStrategy("text", _load_text)

EVIDENCE_LOADERS: Dict[str, EvidenceLoaderStrategy] = {
    ".txt": EvidenceLoaderStrategy("text", _load_text),
    ".json": EvidenceLoaderStrategy("json", _load_json),
    ".xml": EvidenceLoaderStrategy("xml", _load_xml),
    ".yaml": EvidenceLoaderStrategy("yaml", _load_yaml),
    ".yml": EvidenceLoaderStrategy("yaml", _load_yaml),
    ".pdf": EvidenceLoaderStrategy("pdf", _load_pdf),
}

UNPROCESSABLE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
    ".zip",
    ".gz",
    ".tar",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".exe",
    ".bin",
}


class FileSystemEvidenceGateway:
    def resolve_evidence_loader(self, evidence_path):
        _, file_extension = os.path.splitext(evidence_path)
        return EVIDENCE_LOADERS.get(file_extension.lower(), DEFAULT_EVIDENCE_LOADER)

    def build_evidence_metadata(self, strategy):
        return {
            "evidence_type": strategy.evidence_type,
            "schema_version": SCHEMA_VERSION,
        }

    def build_evidence_messages(self, evidence_path, strategy):
        _, file_extension = os.path.splitext(evidence_path)
        file_extension = file_extension.lower()

        if file_extension == "":
            return [
                build_message(
                    "warning",
                    "missing_extension_text_fallback",
                    "Evidence file had no extension and was evaluated as text.",
                    evidence_file=evidence_path,
                )
            ]

        if file_extension not in EVIDENCE_LOADERS:
            return [
                build_message(
                    "warning",
                    "unknown_extension_text_fallback",
                    "Evidence file had an unrecognized extension and was evaluated as text.",
                    evidence_file=evidence_path,
                )
            ]

        return []

    def load_evidence_input(
        self, evidence_path: str
    ) -> Tuple[Any, Dict[str, str], List[Dict[str, str]]]:
        _, file_extension = os.path.splitext(evidence_path)
        file_extension = file_extension.lower()

        if file_extension in UNPROCESSABLE_EXTENSIONS:
            raise EvidenceLoadFailure(
                f"Evidence file extension '{file_extension}' is not supported for evaluation.",
                [
                    build_message(
                        "error",
                        "unprocessable_evidence_type",
                        f"Evidence file extension '{file_extension}' is not supported for evaluation.",
                        evidence_file=evidence_path,
                    )
                ],
            )

        strategy = self.resolve_evidence_loader(evidence_path)
        messages = self.build_evidence_messages(evidence_path, strategy)

        try:
            evidence = strategy.load(evidence_path)
        except FileNotFoundError:
            raise
        except Exception as e:
            messages.append(
                build_message(
                    "error",
                    "evidence_load_error",
                    f"Error loading evidence: {e}",
                    evidence_path,
                )
            )
            raise EvidenceLoadFailure(f"Error loading evidence: {e}", messages)

        return evidence, self.build_evidence_metadata(strategy), messages


DEFAULT_EVIDENCE_GATEWAY = FileSystemEvidenceGateway()
