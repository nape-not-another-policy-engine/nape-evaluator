def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    owner_evaluation = evaluation_index.get("service_owner")
    if owner_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a service_owner evaluation with required: true."
        )

    required_value = owner_evaluation.get("criteria", {}).get("required")
    if required_value is not True:
        return _build_inconclusive_result(
            "This test requires service_owner criteria.required to be true."
        )

    owner_fact = _extract_owner_fact(evidence)
    if owner_fact["status"] != "found":
        return _build_inconclusive_result(
            [owner_fact],
            "Unable to evaluate because the service_owner fact could not be established.",
        )

    return {
        "conclusion": "true",
        "facts": [owner_fact],
        "reason": "service_owner is present, so the required presence check passed.",
    }


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_inconclusive_result("This test expects JSON evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result("This test only supports evaluator schema version 2.")
    if not isinstance(evidence, dict):
        return _build_inconclusive_result("This test expects JSON evidence as a dictionary.")
    return None


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item.get("subject", {})
        name = subject.get("name")
        if isinstance(name, str):
            indexed[name] = item
    return indexed


def _extract_owner_fact(evidence):
    value = evidence.get("component", {}).get("service_owner")
    return {
        "name": "service_owner",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
