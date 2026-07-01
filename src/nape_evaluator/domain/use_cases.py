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

VALID_OUTCOMES = {"pass", "fail", "inconclusive", "error"}


def contextualize_messages(messages, evidence_file, test_file, test_parameters_source=None):
    contextualized = []
    for message in messages:
        updated = dict(message)
        updated["evidence_file"] = evidence_file
        updated["test_file"] = test_file
        updated["test_parameters_source"] = test_parameters_source
        contextualized.append(updated)
    return contextualized


def requested_invocation_contexts(request: EvaluateEvidenceRequest):
    return list(request.test_invocations)


def build_result_record(
    request: EvaluateEvidenceRequest,
    invocation: TestInvocationRequest,
    outcome: str,
    reason: str,
    executed: bool,
):
    return {
        "test": invocation.test_path,
        "evidence_file": request.evidence_path,
        "test_parameters": invocation.test_parameters,
        "test_parameters_source": invocation.test_parameters_source,
        "executed": executed,
        "outcome": outcome,
        "reason": reason,
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
                        invocation.test_parameters_source,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        invocation.blocked_code,
                        invocation.blocked_reason,
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                        test_parameters_source=invocation.test_parameters_source,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        "error",
                        invocation.blocked_reason,
                        executed=False,
                    )
                )
                continue
            try:
                test_of_detail = test_of_detail_gateway.load_test_of_detail(
                    invocation.test_path
                )
                outcome, reason = test_of_detail.evaluate(
                    evidence_data,
                    invocation.test_parameters,
                    metadata,
                )
                if outcome not in VALID_OUTCOMES:
                    invalid_outcome = outcome
                    outcome = "error"
                    reason = (
                        f"Test returned unsupported outcome '{invalid_outcome}'. "
                        "Expected one of: pass, fail, inconclusive, error."
                    )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        outcome,
                        reason,
                        executed=True,
                    )
                )
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                        invocation.test_parameters_source,
                    )
                )
            except FileNotFoundError as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                        invocation.test_parameters_source,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                        test_parameters_source=invocation.test_parameters_source,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        "error",
                        "Unable to find the file(s) for evaluation. " + str(e),
                        executed=False,
                    )
                )
            except ImportError as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                        invocation.test_parameters_source,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_import_error",
                        "Failed to import the necessary files. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                        test_parameters_source=invocation.test_parameters_source,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        "error",
                        "Failed to import the necessary files. " + str(e),
                        executed=False,
                    )
                )
            except Exception as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        invocation.test_path,
                        invocation.test_parameters_source,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_execution_error",
                        "Failed to execute the evidence evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=invocation.test_path,
                        test_parameters_source=invocation.test_parameters_source,
                    )
                )
                results.append(
                    build_result_record(
                        request,
                        invocation,
                        "error",
                        "Failed to execute the evidence evaluation. " + str(e),
                        executed=False,
                    )
                )
        return EvaluateEvidenceResponse(
            count=count,
            results=results,
            messages=messages,
        )

    except FileNotFoundError as e:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=[],
                messages=[
                    build_message(
                        "error",
                        "evidence_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=None,
                    )
                ],
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=[
                build_result_record(
                    request,
                    invocation,
                    "error",
                    "Unable to find the file(s) for evaluation. " + str(e),
                    executed=False,
                )
                for invocation in requested_invocations
            ],
            messages=[
                build_message(
                    "error",
                    "evidence_file_not_found",
                    "Unable to find the file(s) for evaluation. " + str(e),
                    evidence_file=request.evidence_path,
                    test_file=invocation.test_path,
                    test_parameters_source=invocation.test_parameters_source,
                )
                for invocation in requested_invocations
            ],
        )
    except EvidenceLoadFailure as e:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=[],
                messages=e.messages,
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=[
                build_result_record(
                    request,
                    invocation,
                    "error",
                    str(e),
                    executed=False,
                )
                for invocation in requested_invocations
            ],
            messages=[
                dict(
                    message,
                    test_file=invocation.test_path,
                    test_parameters_source=invocation.test_parameters_source,
                )
                for invocation in requested_invocations
                for message in e.messages
            ],
        )
    except Exception as e:
        requested_invocations = requested_invocation_contexts(request)
        if not requested_invocations:
            return EvaluateEvidenceResponse(
                count=0,
                results=[],
                messages=[
                    build_message(
                        "error",
                        "evaluator_execution_error",
                        "Failed to execute the evidence evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=None,
                    )
                ],
            )
        return EvaluateEvidenceResponse(
            count=len(requested_invocations),
            results=[
                build_result_record(
                    request,
                    invocation,
                    "error",
                    "Failed to execute the evidence evaluation. " + str(e),
                    executed=False,
                )
                for invocation in requested_invocations
            ],
            messages=[
                build_message(
                    "error",
                    "evaluator_execution_error",
                    "Failed to execute the evidence evaluation. " + str(e),
                    evidence_file=request.evidence_path,
                    test_file=None,
                )
            ],
        )


def evaluate_evidence_against_tests(
    evidence_path,
    test_requests,
    evidence_gateway,
    test_of_detail_gateway,
):
    test_invocations = []
    for item in test_requests:
        if isinstance(item, TestInvocationRequest):
            test_invocations.append(item)
        else:
            test_invocations.append(TestInvocationRequest.ready(item, {}))

    return evaluate_request(
        EvaluateEvidenceRequest(
            evidence_path=evidence_path,
            test_invocations=test_invocations,
        ),
        evidence_gateway,
        test_of_detail_gateway,
    ).to_cli_output()
