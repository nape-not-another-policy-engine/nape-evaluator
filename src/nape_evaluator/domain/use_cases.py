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


def contextualize_messages(messages, evidence_file, test_file):
    contextualized = []
    for message in messages:
        updated = dict(message)
        updated["evidence_file"] = evidence_file
        updated["test_file"] = test_file
        contextualized.append(updated)
    return contextualized


def requested_invocation_contexts(request: EvaluateEvidenceRequest):
    return list(request.test_invocations)


def build_result_record(
    request: EvaluateEvidenceRequest,
    invocation: TestInvocationRequest,
    executed: bool,
    result,
):
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
    try:
        count = len(request.test_invocations)
        evidence_data, metadata, shared_messages = evidence_gateway.load_evidence_input(
            request.evidence_path
        )
        results = []
        messages = []
        for invocation in request.test_invocations:
            if invocation.is_blocked:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        invocation.blocked_code,
                        invocation.blocked_reason,
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=None,
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
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
            except FileNotFoundError as exc:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(exc),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=None,
                    )
                )
            except ImportError as exc:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_import_error",
                        "Failed to import the necessary files. " + str(exc),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=None,
                    )
                )
            except Exception as exc:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_execution_error",
                        "Failed to execute the evidence evaluation. " + str(exc),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        executed=False,
                        result=None,
                    )
                )
        return EvaluateEvidenceResponse(
            count=count,
            results=tuple(results),
            messages=tuple(messages),
        )

    except FileNotFoundError as exc:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=(),
                messages=(
                    build_message(
                        "error",
                        "evidence_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(exc),
                        evidence_file=request.evidence_path,
                        test_file=None,
                    ),
                ),
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=None,
                )
                for invocation in requested_invocations
            ),
            messages=tuple(
                build_message(
                    "error",
                    "evidence_file_not_found",
                    "Unable to find the file(s) for evaluation. " + str(exc),
                    evidence_file=request.evidence_path,
                    test_file=invocation.test_path,
                )
                for invocation in requested_invocations
            ),
        )
    except EvidenceLoadFailure as exc:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=(),
                messages=tuple(exc.messages),
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=None,
                )
                for invocation in requested_invocations
            ),
            messages=tuple(
                dict(
                    message,
                    test_file=invocation.test_path,
                )
                for invocation in requested_invocations
                for message in exc.messages
            ),
        )
    except Exception as exc:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=(),
                messages=(
                    build_message(
                        "error",
                        "evaluator_execution_error",
                        "Failed to execute the evidence evaluation. " + str(exc),
                        evidence_file=request.evidence_path,
                        test_file=None,
                    ),
                ),
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=tuple(
                build_result_record(
                    request,
                    invocation,
                    executed=False,
                    result=None,
                )
                for invocation in requested_invocations
            ),
            messages=(
                build_message(
                    "error",
                    "evaluator_execution_error",
                    "Failed to execute the evidence evaluation. " + str(exc),
                    evidence_file=request.evidence_path,
                    test_file=None,
                ),
            ),
        )


def evaluate_evidence_against_tests(
    evidence_path,
    test_requests,
    evidence_gateway,
    test_of_detail_gateway,
):
    raw_tests = []
    for item in test_requests:
        if isinstance(item, TestInvocationRequest):
            raw_tests.append(
                {
                    "test": item.test_path,
                    "evaluations": item.evaluations_as_dicts(),
                }
            )
        else:
            raw_tests.append({"test": item, "evaluations": []})

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
