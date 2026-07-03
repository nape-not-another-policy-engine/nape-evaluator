def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    approver_evaluation = evaluation_index.get("approver_identifier")
    if approver_evaluation is None:
        return _build_inconclusive_result(
            "This test requires an approver_identifier evaluation with a required criterion."
        )

    required = _read_required(approver_evaluation)
    if required is not True:
        return _build_inconclusive_result(
            "This test requires approver_identifier criteria.required to be true."
        )

    approver_fact = _extract_approver_fact(evidence)
    if approver_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [approver_fact],
            "reason": "The privileged access evidence did not establish an approver identifier.",
        }
    return {
        "conclusion": "true",
        "facts": [approver_fact],
        "reason": "A privileged access approver identifier is present.",
    }


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_inconclusive_result("This test expects JSON evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result(
            "This test only supports evaluator schema version 2."
        )
    if not isinstance(evidence, dict):
        return _build_inconclusive_result(
            "This test expects JSON evidence as a dictionary."
        )
    return None


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item.get("subject", {})
        name = subject.get("name")
        if isinstance(name, str):
            indexed[name] = item
    return indexed


def _read_required(approver_evaluation):
    value = approver_evaluation.get("criteria", {}).get("required")
    return value if isinstance(value, bool) else None


def _extract_approver_fact(evidence):
    value = evidence.get("privileged_access_review", {}).get("approver_identifier")
    return {
        "name": "approver_identifier",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
