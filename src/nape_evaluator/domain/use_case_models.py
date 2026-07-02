"""Bounded request and response models for the evaluator use case."""

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from nape_evaluator.application.io.output_contract import build_cli_output


SUPPORTED_SUBJECT_DATA_TYPES = {
    "text",
    "integer",
    "number",
    "boolean",
    "date",
    "datetime",
    "duration",
    "array",
    "object",
    "null",
}
SUPPORTED_CRITERIA_KEYS = {
    "minimum",
    "maximum",
    "equals",
    "allowed_values",
    "disallowed_values",
    "required",
}
SUPPORTED_RESULT_CONCLUSIONS = {"true", "false", "inconclusive"}
SUBJECT_NAME_RE = re.compile(r"^[a-z](?:[a-z0-9_]*[a-z0-9])?$")
SUPPORTED_CRITERIA_BY_DATA_TYPE = {
    "text": {"equals", "allowed_values", "disallowed_values", "required"},
    "integer": {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
        "required",
    },
    "number": {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
        "required",
    },
    "boolean": {"equals", "allowed_values", "disallowed_values", "required"},
    "date": {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
        "required",
    },
    "datetime": {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
        "required",
    },
    "duration": {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
        "required",
    },
    "array": {"equals", "required"},
    "object": {"equals", "required"},
    "null": {"equals", "required"},
}


@dataclass(frozen=True)
class RequestValidationError(Exception):
    """Raised when caller-owned request input fails builder validation."""

    code: str
    message: str

    def __str__(self):
        return self.message


@dataclass(frozen=True)
class ResponseValidationError(Exception):
    """Raised when evaluator response data violates the output contract."""

    message: str

    def __str__(self):
        return self.message


@dataclass(frozen=True)
class EvaluationSubject:
    """One caller-declared evaluation subject."""

    name: str
    data_type: str

    def to_dict(self):
        return {
            "name": self.name,
            "data_type": self.data_type,
        }


@dataclass(frozen=True)
class EvaluationInput:
    """One caller-declared subject-plus-criteria evaluation input."""

    subject: EvaluationSubject
    criteria: Dict[str, Any]

    def to_dict(self):
        return {
            "subject": self.subject.to_dict(),
            "criteria": dict(self.criteria),
        }


@dataclass(frozen=True)
class TestInvocationRequest:
    """One requested test invocation accepted by the request builder."""

    test_path: str
    evaluations: Tuple[EvaluationInput, ...]
    blocked_code: Optional[str] = None
    blocked_reason: Optional[str] = None

    @classmethod
    def ready(cls, test_path: str, evaluations: Iterable[EvaluationInput]):
        return cls(
            test_path=test_path,
            evaluations=tuple(evaluations),
        )

    @classmethod
    def blocked(
        cls,
        test_path: str,
        blocked_code: str,
        blocked_reason: str,
        evaluations: Optional[Iterable[EvaluationInput]] = None,
    ):
        return cls(
            test_path=test_path,
            evaluations=tuple(evaluations or ()),
            blocked_code=blocked_code,
            blocked_reason=blocked_reason,
        )

    @property
    def is_blocked(self):
        return self.blocked_code is not None

    def evaluations_as_dicts(self):
        return [item.to_dict() for item in self.evaluations]


@dataclass(frozen=True)
class EvaluateEvidenceRequest:
    """The validated request object that crosses the use-case seam."""

    evidence_path: str
    test_invocations: Tuple[TestInvocationRequest, ...]

    @classmethod
    def builder(cls):
        return EvaluateEvidenceRequestBuilder()


class EvaluateEvidenceRequestBuilder:
    """Builder that validates caller-owned request input before execution."""

    def __init__(self):
        self._evidence_path = None
        self._raw_tests = []

    def evidence_path(self, evidence_path: str):
        self._evidence_path = evidence_path
        return self

    def raw_tests(self, raw_tests: List[Dict[str, Any]]):
        self._raw_tests = list(raw_tests)
        return self

    def add_raw_test_invocation(self, raw_test_invocation: Dict[str, Any]):
        self._raw_tests.append(raw_test_invocation)
        return self

    def try_build(self):
        evidence_path = self._validate_evidence_path()
        raw_tests = self._validate_raw_tests()
        return EvaluateEvidenceRequest(
            evidence_path=evidence_path,
            test_invocations=tuple(self._build_test_invocations(raw_tests)),
        )

    def _validate_evidence_path(self):
        evidence_path = self._evidence_path
        if not isinstance(evidence_path, str) or not evidence_path.strip():
            raise RequestValidationError(
                "invalid_evidence",
                "The request must include a non-empty string evidence path.",
            )
        return evidence_path

    def _validate_raw_tests(self):
        if not isinstance(self._raw_tests, list) or not self._raw_tests:
            raise RequestValidationError(
                "invalid_tests",
                "The request must include a non-empty top-level tests array.",
            )
        return self._raw_tests

    def _build_test_invocations(self, raw_tests: List[Dict[str, Any]]):
        invocations = []
        for index, raw_test in enumerate(raw_tests):
            invocations.append(self._build_test_invocation(index, raw_test))
        return invocations

    def _build_test_invocation(self, index: int, raw_test: Dict[str, Any]):
        if not isinstance(raw_test, dict):
            raise RequestValidationError(
                "invalid_test_item",
                f"tests[{index}] must be an object.",
            )

        unexpected_keys = set(raw_test) - {"test", "evaluations"}
        if unexpected_keys:
            unexpected = ", ".join(sorted(unexpected_keys))
            raise RequestValidationError(
                "invalid_test_item_keys",
                f"tests[{index}] contains unsupported keys: {unexpected}.",
            )

        test_path = raw_test.get("test")
        if not isinstance(test_path, str) or not test_path.strip():
            raise RequestValidationError(
                "invalid_test_path",
                f"tests[{index}].test must be a non-empty string.",
            )

        raw_evaluations = raw_test.get("evaluations")
        if not isinstance(raw_evaluations, list):
            raise RequestValidationError(
                "invalid_evaluations",
                f"tests[{index}].evaluations must be an array.",
            )

        seen_subject_names = set()
        evaluations = []
        for evaluation_index, raw_evaluation in enumerate(raw_evaluations):
            evaluation = self._build_evaluation(index, evaluation_index, raw_evaluation)
            subject_name = evaluation.subject.name
            if subject_name in seen_subject_names:
                raise RequestValidationError(
                    "duplicate_subject_name",
                    f"tests[{index}].evaluations contains duplicate subject.name '{subject_name}'.",
                )
            seen_subject_names.add(subject_name)
            evaluations.append(evaluation)

        return TestInvocationRequest.ready(
            test_path=test_path,
            evaluations=evaluations,
        )

    def _build_evaluation(self, test_index: int, evaluation_index: int, raw_evaluation):
        location = f"tests[{test_index}].evaluations[{evaluation_index}]"
        if not isinstance(raw_evaluation, dict):
            raise RequestValidationError(
                "invalid_evaluation",
                f"{location} must be an object.",
            )

        if set(raw_evaluation) != {"subject", "criteria"}:
            raise RequestValidationError(
                "invalid_evaluation_keys",
                f"{location} must contain exactly subject and criteria.",
            )

        subject = self._build_subject(
            f"{location}.subject",
            raw_evaluation["subject"],
        )
        criteria = self._build_criteria(
            f"{location}.criteria",
            subject.data_type,
            raw_evaluation["criteria"],
        )
        return EvaluationInput(subject=subject, criteria=criteria)

    def _build_subject(self, location: str, raw_subject: Dict[str, Any]):
        if not isinstance(raw_subject, dict):
            raise RequestValidationError(
                "invalid_subject",
                f"{location} must be an object.",
            )

        if set(raw_subject) != {"name", "data_type"}:
            raise RequestValidationError(
                "invalid_subject_keys",
                f"{location} must contain exactly name and data_type.",
            )

        name = raw_subject.get("name")
        if not isinstance(name, str) or not SUBJECT_NAME_RE.match(name):
            raise RequestValidationError(
                "invalid_subject_name",
                f"{location}.name must be lowercase snake_case ASCII, start with a letter, and end with an alphanumeric.",
            )

        data_type = raw_subject.get("data_type")
        if data_type not in SUPPORTED_SUBJECT_DATA_TYPES:
            supported = ", ".join(sorted(SUPPORTED_SUBJECT_DATA_TYPES))
            raise RequestValidationError(
                "invalid_subject_data_type",
                f"{location}.data_type must be one of: {supported}.",
            )

        return EvaluationSubject(name=name, data_type=data_type)

    def _build_criteria(self, location: str, data_type: str, raw_criteria: Dict[str, Any]):
        if not isinstance(raw_criteria, dict) or not raw_criteria:
            raise RequestValidationError(
                "invalid_criteria",
                f"{location} must be a non-empty object.",
            )

        unsupported_keys = set(raw_criteria) - SUPPORTED_CRITERIA_KEYS
        if unsupported_keys:
            unsupported = ", ".join(sorted(unsupported_keys))
            raise RequestValidationError(
                "invalid_criteria_keys",
                f"{location} contains unsupported keys: {unsupported}.",
            )

        incompatible_keys = set(raw_criteria) - SUPPORTED_CRITERIA_BY_DATA_TYPE[data_type]
        if incompatible_keys:
            incompatible = ", ".join(sorted(incompatible_keys))
            raise RequestValidationError(
                "incompatible_criteria",
                f"{location} contains criteria incompatible with subject.data_type {data_type}: {incompatible}.",
            )

        criteria = {}
        for key, value in raw_criteria.items():
            self._validate_criteria_value(location, data_type, key, value)
            criteria[key] = value
        return criteria

    def _validate_criteria_value(self, location: str, data_type: str, key: str, value: Any):
        field_location = f"{location}.{key}"
        if key == "required":
            if not isinstance(value, bool):
                raise RequestValidationError(
                    "invalid_required",
                    f"{field_location} must be a boolean.",
                )
            return

        if key in {"minimum", "maximum", "equals"}:
            if not _value_matches_data_type(data_type, value):
                raise RequestValidationError(
                    "invalid_criteria_value",
                    f"{field_location} must match subject.data_type {data_type}.",
                )
            return

        if key in {"allowed_values", "disallowed_values"}:
            if not isinstance(value, list):
                raise RequestValidationError(
                    "invalid_criteria_values",
                    f"{field_location} must be an array.",
                )
            for item in value:
                if not _value_matches_data_type(data_type, item):
                    raise RequestValidationError(
                        "invalid_criteria_values",
                        f"{field_location} entries must match subject.data_type {data_type}.",
                    )
            return


def _value_matches_data_type(data_type: str, value: Any):
    if data_type == "text":
        return isinstance(value, str)
    if data_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if data_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if data_type == "boolean":
        return isinstance(value, bool)
    if data_type in {"date", "datetime", "duration"}:
        return isinstance(value, str)
    if data_type == "array":
        return isinstance(value, list)
    if data_type == "object":
        return isinstance(value, dict)
    if data_type == "null":
        return value is None
    return False


@dataclass(frozen=True)
class EvaluateEvidenceResponse:
    """The validated evaluator response before CLI serialization."""

    count: int
    results: Tuple[Dict[str, Any], ...]
    messages: Tuple[Dict[str, Any], ...]

    def __post_init__(self):
        if self.count != len(self.results):
            raise ResponseValidationError(
                "EvaluateEvidenceResponse.count must match the number of results."
            )
        for result in self.results:
            self._validate_result_record(result)
        for message in self.messages:
            self._validate_message_record(message)

    @classmethod
    def normalize_completed_result(cls, raw_result: Any):
        """Normalize completed test output into the bounded result contract."""

        try:
            return cls._validate_completed_result_contract(raw_result)
        except ResponseValidationError as exc:
            return {
                "conclusion": "inconclusive",
                "facts": [],
                "reason": (
                    "The test completed, but returned an invalid result contract, "
                    f"so the conclusion is inconclusive. {exc}"
                ),
            }

    @classmethod
    def _validate_result_record(cls, result: Dict[str, Any]):
        if not isinstance(result, dict):
            raise ResponseValidationError("Each result item must be an object.")
        for required_key in ("test", "evidence", "evaluations", "execution", "result"):
            if required_key not in result:
                raise ResponseValidationError(
                    f"Each result item must include {required_key}."
                )

        if not isinstance(result["test"], str) or not result["test"]:
            raise ResponseValidationError("Result test must be a non-empty string.")
        if not isinstance(result["evidence"], str) or not result["evidence"]:
            raise ResponseValidationError("Result evidence must be a non-empty string.")
        if not isinstance(result["evaluations"], list):
            raise ResponseValidationError("Result evaluations must be an array.")

        execution = result["execution"]
        if not isinstance(execution, dict):
            raise ResponseValidationError("Result execution must be an object.")
        executed = execution.get("executed")
        status = execution.get("status")
        if not isinstance(executed, bool):
            raise ResponseValidationError("execution.executed must be a boolean.")
        if status not in {"completed", "blocked"}:
            raise ResponseValidationError(
                "execution.status must be completed or blocked."
            )
        if executed and status != "completed":
            raise ResponseValidationError(
                "execution.status must be completed when execution.executed is true."
            )
        if not executed and status != "blocked":
            raise ResponseValidationError(
                "execution.status must be blocked when execution.executed is false."
            )

        if executed:
            cls._validate_completed_result_contract(result["result"])
        else:
            cls._validate_blocked_result_contract(result["result"])

    @classmethod
    def _validate_blocked_result_contract(cls, raw_result: Any):
        if not isinstance(raw_result, dict):
            raise ResponseValidationError(
                "Blocked results must include an object with conclusion, facts, and reason."
            )

        result = cls._validate_completed_result_contract(raw_result)
        if result["conclusion"] != "inconclusive":
            raise ResponseValidationError(
                "Blocked results must use conclusion 'inconclusive'."
            )
        return result

    @classmethod
    def _validate_completed_result_contract(cls, raw_result: Any):
        if not isinstance(raw_result, dict):
            raise ResponseValidationError(
                "Test returned invalid result contract. Expected an object with conclusion, facts, and reason."
            )
        if set(raw_result) != {"conclusion", "facts", "reason"}:
            raise ResponseValidationError(
                "Test returned invalid result contract. Expected exactly conclusion, facts, and reason."
            )

        conclusion = raw_result.get("conclusion")
        if conclusion not in SUPPORTED_RESULT_CONCLUSIONS:
            supported = ", ".join(sorted(SUPPORTED_RESULT_CONCLUSIONS))
            raise ResponseValidationError(
                f"Test returned unsupported conclusion '{conclusion}'. Expected one of: {supported}."
            )

        facts = raw_result.get("facts")
        if not isinstance(facts, list):
            raise ResponseValidationError("result.facts must be an array.")
        for fact in facts:
            if not isinstance(fact, dict):
                raise ResponseValidationError("Each result fact must be an object.")
            for required_key in ("name", "value_type", "status"):
                if required_key not in fact or not isinstance(fact[required_key], str):
                    raise ResponseValidationError(
                        f"Each result fact must include string {required_key}."
                    )

        reason = raw_result.get("reason")
        if not isinstance(reason, str) or not reason:
            raise ResponseValidationError("result.reason must be a non-empty string.")

        return {
            "conclusion": conclusion,
            "facts": facts,
            "reason": reason,
        }

    @classmethod
    def _validate_message_record(cls, message: Dict[str, Any]):
        if not isinstance(message, dict):
            raise ResponseValidationError("Each evaluator message must be an object.")

        required_keys = {
            "scope",
            "level",
            "source",
            "code",
            "message",
            "evidence_file",
            "test_file",
            "affected_tests",
            "stack_trace",
        }
        if set(message) != required_keys:
            raise ResponseValidationError(
                "Each evaluator message must include exactly scope, level, source, code, message, evidence_file, test_file, affected_tests, and stack_trace."
            )

        if message["scope"] not in {"request", "test"}:
            raise ResponseValidationError(
                "Evaluator message scope must be request or test."
            )

        if message["level"] not in {"info", "warning", "error"}:
            raise ResponseValidationError(
                "Evaluator message level must be info, warning, or error."
            )

        if message["source"] != "evaluator":
            raise ResponseValidationError(
                "Evaluator message source must be 'evaluator'."
            )

        for field_name in ("code", "message"):
            value = message[field_name]
            if not isinstance(value, str) or not value:
                raise ResponseValidationError(
                    f"Evaluator message {field_name} must be a non-empty string."
                )

        if message["evidence_file"] is not None and not isinstance(
            message["evidence_file"], str
        ):
            raise ResponseValidationError(
                "Evaluator message evidence_file must be a string or null."
            )

        if message["test_file"] is not None and not isinstance(message["test_file"], str):
            raise ResponseValidationError(
                "Evaluator message test_file must be a string or null."
            )

        affected_tests = message["affected_tests"]
        if affected_tests is not None:
            if not isinstance(affected_tests, list) or not all(
                isinstance(item, str) and item for item in affected_tests
            ):
                raise ResponseValidationError(
                    "Evaluator message affected_tests must be an array of non-empty strings or null."
                )

        stack_trace = message["stack_trace"]
        if stack_trace is not None and not isinstance(stack_trace, str):
            raise ResponseValidationError(
                "Evaluator message stack_trace must be a string or null."
            )

        if message["scope"] == "request":
            if message["test_file"] is not None:
                raise ResponseValidationError(
                    "Request-scoped messages must use test_file null."
                )
            if not isinstance(affected_tests, list) or not affected_tests:
                raise ResponseValidationError(
                    "Request-scoped messages must include a non-empty affected_tests array."
                )

        if message["scope"] == "test":
            if not isinstance(message["test_file"], str) or not message["test_file"]:
                raise ResponseValidationError(
                    "Test-scoped messages must include a non-empty test_file."
                )
            if affected_tests is not None:
                raise ResponseValidationError(
                    "Test-scoped messages must use affected_tests null."
                )

    def to_cli_output(self):
        """Serialize the validated response into the CLI JSON shape."""

        return build_cli_output(self.count, list(self.results), list(self.messages))
