from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from nape_evaluator.application.io.output_contract import build_cli_output


@dataclass(frozen=True)
class TestInvocationRequest:
    test_path: str
    test_parameters: Optional[Dict[str, Any]]
    test_parameters_source: Optional[str] = None
    blocked_code: Optional[str] = None
    blocked_reason: Optional[str] = None

    @classmethod
    def ready(
        cls,
        test_path: str,
        test_parameters: Dict[str, Any],
        test_parameters_source: Optional[str] = None,
    ):
        return cls(
            test_path=test_path,
            test_parameters=test_parameters,
            test_parameters_source=test_parameters_source,
        )

    @classmethod
    def blocked(
        cls,
        test_path: str,
        blocked_code: str,
        blocked_reason: str,
        test_parameters_source: Optional[str] = None,
        test_parameters: Optional[Dict[str, Any]] = None,
    ):
        return cls(
            test_path=test_path,
            test_parameters=test_parameters,
            test_parameters_source=test_parameters_source,
            blocked_code=blocked_code,
            blocked_reason=blocked_reason,
        )

    @property
    def is_blocked(self):
        return self.blocked_code is not None


@dataclass(frozen=True)
class EvaluateEvidenceRequest:
    evidence_path: str
    test_invocations: List[TestInvocationRequest]


@dataclass(frozen=True)
class EvaluateEvidenceResponse:
    count: int
    results: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

    def to_cli_output(self):
        return build_cli_output(self.count, self.results, self.messages)
