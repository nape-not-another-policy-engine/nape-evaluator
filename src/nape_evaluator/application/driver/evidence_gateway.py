"""Filesystem-backed evidence loading for the evaluator."""

from dataclasses import dataclass
import json
import os
import traceback
from typing import Any, Callable, Dict, List, Tuple
import xml.etree.ElementTree as ET

from nape_evaluator.application.io.output_contract import build_message
from nape_evaluator.domain.gateways import EvidenceLoadFailure

SCHEMA_VERSION = "2"


@dataclass(frozen=True)
class EvidenceLoaderStrategy:
    """Maps one file-extension class to an evidence loader function."""

    evidence_type: str
    load: Callable[[str], Any]


def _load_text(evidence_path: str) -> List[str]:
    with open(evidence_path, "r", encoding="utf-8") as handle:
        return handle.readlines()


def _load_json(evidence_path: str) -> Any:
    with open(evidence_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_xml(evidence_path: str) -> Any:
    tree = ET.parse(evidence_path)
    return tree.getroot()


def _load_yaml(evidence_path: str) -> Any:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("YAML support requires PyYAML to be installed.") from exc

    with open(evidence_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_pdf(evidence_path: str) -> List[str]:
    try:
        import PyPDF2
    except ImportError as exc:
        raise RuntimeError("PDF support requires PyPDF2 to be installed.") from exc

    with open(evidence_path, "rb") as handle:
        reader = PyPDF2.PdfReader(handle)
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
    """Load evaluator evidence from the local filesystem."""

    def resolve_evidence_loader(self, evidence_path: str) -> EvidenceLoaderStrategy:
        """Choose the loader strategy for one evidence path."""

        _, file_extension = os.path.splitext(evidence_path)
        return EVIDENCE_LOADERS.get(file_extension.lower(), DEFAULT_EVIDENCE_LOADER)

    def build_evidence_metadata(
        self, strategy: EvidenceLoaderStrategy
    ) -> Dict[str, str]:
        """Build the evaluator-owned metadata passed into the test contract."""

        return {
            "evidence_type": strategy.evidence_type,
            "schema_version": SCHEMA_VERSION,
        }

    def build_evidence_messages(
        self, evidence_path: str, strategy: EvidenceLoaderStrategy
    ) -> List[Dict[str, Any]]:
        """Build request-scoped evaluator notices for evidence fallback behavior."""

        _, file_extension = os.path.splitext(evidence_path)
        file_extension = file_extension.lower()

        if file_extension == "":
            return [
                build_message(
                    "warning",
                    "missing_extension_text_fallback",
                    "Evidence file had no extension and was evaluated as text.",
                    evidence_file=evidence_path,
                    scope="request",
                    test_file=None,
                )
            ]

        if file_extension not in EVIDENCE_LOADERS:
            return [
                build_message(
                    "warning",
                    "unknown_extension_text_fallback",
                    "Evidence file had an unrecognized extension and was evaluated as text.",
                    evidence_file=evidence_path,
                    scope="request",
                    test_file=None,
                )
            ]

        return []

    def load_evidence_input(
        self, evidence_path: str
    ) -> Tuple[Any, Dict[str, str], List[Dict[str, Any]]]:
        """Load evidence content, metadata, and request-scoped evaluator notices."""

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
                        scope="request",
                        test_file=None,
                    )
                ],
            )

        strategy = self.resolve_evidence_loader(evidence_path)
        messages = self.build_evidence_messages(evidence_path, strategy)

        try:
            evidence = strategy.load(evidence_path)
        except FileNotFoundError:
            raise
        except Exception as exc:
            messages.append(
                build_message(
                    "error",
                    "evidence_load_error",
                    f"Error loading evidence: {exc}",
                    evidence_file=evidence_path,
                    scope="request",
                    test_file=None,
                    stack_trace=traceback.format_exc(),
                )
            )
            raise EvidenceLoadFailure(f"Error loading evidence: {exc}", messages)

        return evidence, self.build_evidence_metadata(strategy), messages


DEFAULT_EVIDENCE_GATEWAY = FileSystemEvidenceGateway()
