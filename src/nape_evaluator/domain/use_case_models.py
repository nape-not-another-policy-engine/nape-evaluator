from dataclasses import dataclass
from typing import Any, Dict, List

from nape_evaluator.application.io.output_contract import build_cli_output


@dataclass(frozen=True)
class EvaluateEvidenceRequest:
    evidence_path: str
    test_paths: List[str]


@dataclass(frozen=True)
class EvaluateEvidenceResponse:
    count: int
    results: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

    def to_cli_output(self):
        return build_cli_output(self.count, self.results, self.messages)
