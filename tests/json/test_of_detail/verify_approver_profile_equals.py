def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    approver_evaluation = evaluation_index.get("approver_profile")
    if approver_evaluation is None:
        return _build_error_result(
            "This test requires an approver_profile evaluation with an equals criterion."
        )

    expected_profile = approver_evaluation.get("criteria", {}).get("equals")
    if not isinstance(expected_profile, dict):
        return _build_error_result(
            "This test requires approver_profile criteria.equals to be an object."
        )

    approver_fact = _extract_approver_profile_fact(evidence)
    if approver_fact["status"] != "found":
        return _build_inconclusive_result(
            [approver_fact],
            "Unable to evaluate because the approver_profile fact could not be established.",
        )

    return _evaluate_equals(approver_fact, expected_profile)


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_error_result("This test expects JSON evidence.")
    if metadata.get("schema_version") != "2":
        return _build_error_result("This test only supports evaluator schema version 2.")
    if not isinstance(evidence, dict):
        return _build_error_result("This test expects JSON evidence as a dictionary.")
    return None


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item.get("subject", {})
        name = subject.get("name")
        if isinstance(name, str):
            indexed[name] = item
    return indexed


def _extract_approver_profile_fact(evidence):
    value = evidence.get("access_grant", {}).get("approver_profile")
    if value is None:
        return {
            "name": "approver_profile",
            "value": None,
            "value_type": "object",
            "status": "not_found",
        }
    if not isinstance(value, dict):
        return {
            "name": "approver_profile",
            "value": None,
            "value_type": "object",
            "status": "invalid",
        }
    return {
        "name": "approver_profile",
        "value": value,
        "value_type": "object",
        "status": "found",
    }


def _evaluate_equals(approver_fact, expected_profile):
    actual = approver_fact["value"]
    if actual == expected_profile:
        return {
            "conclusion": "true",
            "facts": [approver_fact],
            "reason": "approver_profile exactly matches the expected object.",
        }
    return {
        "conclusion": "false",
        "facts": [approver_fact],
        "reason": "approver_profile does not exactly match the expected object.",
    }


def _build_inconclusive_result(facts, reason):
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }


def _build_error_result(reason):
    return {
        "conclusion": "error",
        "facts": [],
        "reason": reason,
    }
