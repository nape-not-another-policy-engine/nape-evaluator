"""Use-case orchestration for evaluating evidence against requested tests."""

import traceback
from typing import Any, Dict, Iterable, List, Optional, Sequence

from nape_evaluator.application.io.output_contract import build_message
from nape_evaluator.domain.gateways import (
    EvidenceGateway,
    EvidenceLoadFailure,
    TestOfDetailGateway,
)
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    EvaluateEvidenceResponse,
    TestInvocationRequest,
)


def contextualize_messages(
    messages: Iterable[Dict[str, Any]],
    evidence_file: str,
    test_paths: Sequence[str],
) -> List[Dict[str, Any]]:
    """Contextualize shared evaluator messages as distinct request-scoped events."""

    affected_tests = list(test_paths)
    contextualized = []
    for message in messages:
        contextualized.append(
            dict(
                message,
                scope="request",
                evidence_file=evidence_file,
                test_file=None,
                affected_tests=affected_tests,
                stack_trace=message.get("stack_trace"),
            )
        )
    return contextualized


def requested_invocation_contexts(
    request: EvaluateEvidenceRequest,
) -> List[TestInvocationRequest]:
    """Return the requested test invocation contexts for one use-case call."""

    return list(request.test_invocations)


def build_result_record(
    request: EvaluateEvidenceRequest,
    invocation: TestInvocationRequest,
    executed: bool,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Build one per-test result row in the public evaluator output shape."""

    return {
        "test": invocation.test_path,
        "evidence": request.evidence_path,
        "evaluations": invocation.evaluations_as_dicts(),
        "execution": {
            "executed": executed,
            "status": "completed" if executed else "blocked",
        },
        "result": result,
    }


def evaluate_request(
    request: EvaluateEvidenceRequest,
    evidence_gateway: EvidenceGateway,
    test_of_detail_gateway: TestOfDetailGateway,
) -> EvaluateEvidenceResponse:
    """Evaluate one evidence input against one or more requested tests."""

    requested_invocations = requested_invocation_contexts(request)
    affected_tests = _requested_test_paths(requested_invocations)

    try:
        count = len(requested_invocations)
        evidence_data, metadata, shared_messages = evidence_gateway.load_evidence_input(
            request.evidence_path
        )
        results = []
        messages = contextualize_messages(
            shared_messages,
            request.evidence_path,
            affected_tests,
        )

        for invocation in requested_invocations:
            if invocation.is_blocked:
                messages.append(
                    _build_test_scoped_message(
                        invocation.blocked_code or "blocked_invocation",
                        invocation.blocked_reason
                        or "The requested test invocation is blocked.",
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=_build_blocked_inconclusive_result(
                            invocation.blocked_code or "blocked_invocation",
                            invocation.blocked_reason,
                        ),
                    )
                )
                continue

            try:
                test_of_detail = test_of_detail_gateway.load_test_of_detail(
                    invocation.test_path
                )
                raw_result = test_of_detail.evaluate(
                    evidence_data,
                    invocation.evaluations_as_dicts(),
                    metadata,
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=True,
                        result=EvaluateEvidenceResponse.normalize_completed_result(
                            raw_result
                        ),
                    )
                )
            except FileNotFoundError as exc:
                messages.append(
                    _build_test_scoped_message(
                        "test_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(exc),
                        request.evidence_path,
                        invocation.test_path,
                        stack_trace=traceback.format_exc(),
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=_build_blocked_inconclusive_result("test_file_not_found"),
                    )
                )
            except ImportError as exc:
                messages.append(
                    _build_test_scoped_message(
                        "test_import_error",
                        "Failed to import the necessary files. " + str(exc),
                        request.evidence_path,
                        invocation.test_path,
                        stack_trace=traceback.format_exc(),
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=_build_blocked_inconclusive_result("test_import_error"),
                    )
                )
            except Exception as exc:
                messages.append(
                    _build_test_scoped_message(
                        "test_execution_error",
                        "Failed to execute the evidence evaluation. " + str(exc),
                        request.evidence_path,
                        invocation.test_path,
                        stack_trace=traceback.format_exc(),
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=_build_blocked_inconclusive_result("test_execution_error"),
                    )
                )

        return EvaluateEvidenceResponse(
            count=count,
            results=tuple(results),
            messages=tuple(messages),
        )

    except FileNotFoundError as exc:
        message = _build_request_scoped_message(
            "evidence_file_not_found",
            "Unable to find the file(s) for evaluation. " + str(exc),
            request.evidence_path,
            affected_tests,
            stack_trace=traceback.format_exc(),
        )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=_build_blocked_inconclusive_result("evidence_file_not_found"),
                )
                for invocation in requested_invocations
            ),
            messages=(message,),
        )
    except EvidenceLoadFailure as exc:
        primary_code = _primary_failure_code(exc.messages, default="evidence_load_error")
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=_build_blocked_inconclusive_result(primary_code),
                )
                for invocation in requested_invocations
            ),
            messages=tuple(
                contextualize_messages(
                    exc.messages,
                    request.evidence_path,
                    affected_tests,
                )
            ),
        )
    except Exception as exc:
        message = _build_request_scoped_message(
            "evaluator_execution_error",
            "Failed to execute the evidence evaluation. " + str(exc),
            request.evidence_path,
            affected_tests,
            stack_trace=traceback.format_exc(),
        )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=_build_blocked_inconclusive_result(
                        "evaluator_execution_error"
                    ),
                )
                for invocation in requested_invocations
            ),
            messages=(message,),
        )


def evaluate_evidence_against_tests(
    evidence_path: str,
    test_requests: Sequence[Any],
    evidence_gateway: EvidenceGateway,
    test_of_detail_gateway: TestOfDetailGateway,
) -> Dict[str, Any]:
    """Convenience wrapper that builds a request and returns CLI-shaped JSON."""

    raw_tests = []
    for item in test_requests:
        if isinstance(item, TestInvocationRequest):
            raw_tests.append(
                {
                    "test": item.test_path,
                    "evaluations": item.evaluations_as_dicts(),
                }
            )
        elif isinstance(item, dict):
            raw_tests.append(item)
        else:
            raise TypeError(
                "test_requests items must be TestInvocationRequest or raw invocation dict objects."
            )

    request = (
        EvaluateEvidenceRequest.builder()
        .evidence_path(evidence_path)
        .raw_tests(raw_tests)
        .try_build()
    )
    return evaluate_request(
        request,
        evidence_gateway,
        test_of_detail_gateway,
    ).to_cli_output()


def _requested_test_paths(
    invocations: Sequence[TestInvocationRequest],
) -> List[str]:
    return [invocation.test_path for invocation in invocations]


def _build_request_scoped_message(
    code: str,
    message: str,
    evidence_file: str,
    affected_tests: Sequence[str],
    *,
    stack_trace: Optional[str] = None,
) -> Dict[str, Any]:
    return build_message(
        "error",
        code,
        message,
        evidence_file=evidence_file,
        test_file=None,
        scope="request",
        affected_tests=list(affected_tests),
        stack_trace=stack_trace,
    )


def _build_test_scoped_message(
    code: str,
    message: str,
    evidence_file: str,
    test_file: str,
    *,
    stack_trace: Optional[str] = None,
) -> Dict[str, Any]:
    return build_message(
        "error",
        code,
        message,
        evidence_file=evidence_file,
        test_file=test_file,
        scope="test",
        affected_tests=None,
        stack_trace=stack_trace,
    )


def _build_blocked_inconclusive_result(
    code: str,
    detail: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": _format_blocked_reason(code, detail),
    }


def _format_blocked_reason(code: str, detail: Optional[str] = None) -> str:
    reasons = {
        "blocked_invocation": "The requested test invocation was blocked before execution.",
        "evidence_file_not_found": "The evaluator could not load the evidence file because it was not found.",
        "unprocessable_evidence_type": "The evaluator could not process the evidence file type.",
        "evidence_load_error": "The evaluator could not load the evidence file.",
        "test_file_not_found": "The evaluator could not find the test file.",
        "test_import_error": "The evaluator could not import the test file.",
        "test_execution_error": "The evaluator encountered an execution error before the test could finish.",
        "evaluator_execution_error": "The evaluator encountered an execution error before the test could finish.",
    }

    detail_reason = reasons.get(code)
    if detail_reason is None and detail:
        detail_reason = detail
    if detail_reason is None:
        detail_reason = "The evaluator could not complete the test."

    return (
        "The test could not be completed, so the conclusion is inconclusive. "
        + detail_reason
    )


def _primary_failure_code(
    messages: Iterable[Dict[str, Any]],
    *,
    default: str,
) -> str:
    for message in messages:
        if message.get("level") == "error" and isinstance(message.get("code"), str):
            return message["code"]
    return default
