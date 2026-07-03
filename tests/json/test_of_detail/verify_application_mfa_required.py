def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    mfa_evaluation = evaluation_index.get("mfa_required")
    if mfa_evaluation is None:
        return _build_inconclusive_result(
            "This test requires an mfa_required evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(mfa_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires mfa_required criteria.equals to be boolean."
        )

    mfa_fact = _extract_mfa_fact(evidence)
    if mfa_fact["status"] != "found":
        return _build_inconclusive_result(
            [mfa_fact],
            "Unable to evaluate because the mfa_required fact could not be established.",
        )

    return _evaluate_equals(mfa_fact, expected_value)


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


def _read_boolean_equals(evaluation):
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_mfa_fact(evidence):
    value = evidence.get("application_release", {}).get("mfa_required")
    if value is None:
        return {
            "name": "mfa_required",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "mfa_required",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "mfa_required",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(mfa_fact, expected_value):
    actual = mfa_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [mfa_fact],
            "reason": f"mfa_required is {actual}, which matches the expected value.",
        }
    return {
        "conclusion": "false",
        "facts": [mfa_fact],
        "reason": f"mfa_required is {actual}, which does not match the expected value {expected_value}.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
