def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    status_evaluation = evaluation_index.get("release_status")
    if status_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a release_status evaluation with an allowed_values criterion."
        )

    allowed_values = _read_allowed_values(status_evaluation)
    if not allowed_values:
        return _build_inconclusive_result(
            "This test requires release_status criteria.allowed_values to be a non-empty text array."
        )

    status_fact = _extract_release_status_fact(evidence)
    if status_fact["status"] != "found":
        return _build_inconclusive_result(
            [status_fact],
            "Unable to evaluate because the release_status fact could not be established.",
        )

    return _evaluate_allowed_values(status_fact, allowed_values)


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


def _read_allowed_values(evaluation):
    values = evaluation.get("criteria", {}).get("allowed_values")
    if not isinstance(values, list) or not values:
        return None
    for item in values:
        if not isinstance(item, str):
            return None
    return list(values)


def _extract_release_status_fact(evidence):
    value = evidence.get("component", {}).get("release_status")
    return {
        "name": "release_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _evaluate_allowed_values(status_fact, allowed_values):
    actual = status_fact["value"]
    if actual in allowed_values:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"release_status is '{actual}', which is in the allowed value set.",
        }
    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": f"release_status is '{actual}', which is not in the allowed value set.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
