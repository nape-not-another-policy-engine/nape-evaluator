from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Tuple


@dataclass(frozen=True)
class EvidenceLoadFailure(Exception):
    message: str
    messages: List[Dict[str, Any]]

    def __str__(self):
        return self.message


class EvidenceGateway(Protocol):
    def load_evidence_input(
        self, evidence_path: str
    ) -> Tuple[Any, Dict[str, str], List[Dict[str, Any]]]:
        ...


class TestOfDetailGateway(Protocol):
    def load_test_of_detail(self, test_path: str) -> Any:
        ...
