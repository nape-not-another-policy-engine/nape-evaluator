def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    roles_evaluation = evaluation_index.get("reviewer_roles")
    if roles_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a reviewer_roles evaluation with an equals criterion."
        )

    expected_roles = roles_evaluation.get("criteria", {}).get("equals")
    if not isinstance(expected_roles, list):
        return _build_inconclusive_result(
            "This test requires reviewer_roles criteria.equals to be an array."
        )

    roles_fact = _extract_reviewer_roles_fact(evidence)
    if roles_fact["status"] != "found":
        return _build_inconclusive_result(
            [roles_fact],
            "Unable to evaluate because the reviewer_roles fact could not be established.",
        )

    return _evaluate_equals(roles_fact, expected_roles)


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


def _extract_reviewer_roles_fact(evidence):
    value = evidence.get("access_grant", {}).get("reviewer_roles")
    if value is None:
        return {
            "name": "reviewer_roles",
            "value": None,
            "value_type": "array",
            "status": "not_found",
        }
    if not isinstance(value, list):
        return {
            "name": "reviewer_roles",
            "value": None,
            "value_type": "array",
            "status": "invalid",
        }
    return {
        "name": "reviewer_roles",
        "value": value,
        "value_type": "array",
        "status": "found",
    }


def _evaluate_equals(roles_fact, expected_roles):
    actual = roles_fact["value"]
    if actual == expected_roles:
        return {
            "conclusion": "true",
            "facts": [roles_fact],
            "reason": "reviewer_roles exactly matches the expected array.",
        }
    return {
        "conclusion": "false",
        "facts": [roles_fact],
        "reason": "reviewer_roles does not exactly match the expected array.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
