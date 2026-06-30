from nape_evaluator.application.io.output_contract import build_message
from nape_evaluator.domain.gateways import (
    EvidenceGateway,
    EvidenceLoadFailure,
    TestOfDetailGateway,
)
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    EvaluateEvidenceResponse,
)

VALID_OUTCOMES = {"pass", "fail", "inconclusive", "error"}


def contextualize_messages(messages, evidence_file, test_file):
    contextualized = []
    for message in messages:
        updated = dict(message)
        updated["evidence_file"] = evidence_file
        updated["test_file"] = test_file
        contextualized.append(updated)
    return contextualized


def evaluate_request(
    request: EvaluateEvidenceRequest,
    evidence_gateway: EvidenceGateway,
    test_of_detail_gateway: TestOfDetailGateway,
) -> EvaluateEvidenceResponse:
    try:
        count = len(request.test_paths)
        evidence_data, metadata, shared_messages = evidence_gateway.load_evidence_input(
            request.evidence_path
        )
        results = []
        messages = []
        for test_path in request.test_paths:
            try:
                test_of_detail = test_of_detail_gateway.load_test_of_detail(test_path)
                outcome, reason = test_of_detail.evaluate(evidence_data, metadata)
                if outcome not in VALID_OUTCOMES:
                    invalid_outcome = outcome
                    outcome = "error"
                    reason = (
                        f"Test returned unsupported outcome '{invalid_outcome}'. "
                        "Expected one of: pass, fail, inconclusive, error."
                    )
                results.append(
                    {
                        "test": test_path,
                        "outcome": outcome,
                        "reason": reason,
                    }
                )
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        test_path,
                    )
                )
            except FileNotFoundError as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_file_not_found",
                        "Unable to find the file(s) for evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=test_path,
                    )
                )
            except ImportError as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_import_error",
                        "Failed to import the necessary files. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=test_path,
                    )
                )
            except Exception as e:
                messages.extend(
                    contextualize_messages(
                        shared_messages,
                        request.evidence_path,
                        test_path,
                    )
                )
                messages.append(
                    build_message(
                        "error",
                        "test_execution_error",
                        "Failed to execute the evidence evaluation. " + str(e),
                        evidence_file=request.evidence_path,
                        test_file=test_path,
                    )
                )
        return EvaluateEvidenceResponse(
            count=count,
            results=results,
            messages=messages,
        )

    except FileNotFoundError as e:
        requested_tests = request.test_paths if request.test_paths else [None]
        return EvaluateEvidenceResponse(
            count=len([t for t in requested_tests if t is not None]),
            results=[],
            messages=[
                build_message(
                    "error",
                    "evidence_file_not_found",
                    "Unable to find the file(s) for evaluation. " + str(e),
                    evidence_file=request.evidence_path,
                    test_file=test_path,
                )
                for test_path in requested_tests
            ],
        )
    except EvidenceLoadFailure as e:
        requested_tests = request.test_paths if request.test_paths else [None]
        return EvaluateEvidenceResponse(
            count=len([t for t in requested_tests if t is not None]),
            results=[],
            messages=[
                dict(message, test_file=test_path)
                for test_path in requested_tests
                for message in e.messages
            ],
        )
    except Exception as e:
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


def evaluate_evidence_against_tests(
    evidence_path,
    test_paths,
    evidence_gateway,
    test_of_detail_gateway,
):
    return evaluate_request(
        EvaluateEvidenceRequest(
            evidence_path=evidence_path,
            test_paths=list(test_paths),
        ),
        evidence_gateway,
        test_of_detail_gateway,
    ).to_cli_output()
