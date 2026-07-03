def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    match_evaluation = evaluation_index.get("cross_system_state_match")
    if match_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a cross_system_state_match evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(match_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires cross_system_state_match criteria.equals to be boolean."
        )

    match_fact = _extract_match_fact(evidence)
    if match_fact["status"] != "found":
        return _build_inconclusive_result(
            [match_fact],
            "Unable to evaluate because the cross_system_state_match fact could not be established.",
        )

    return _evaluate_equals(match_fact, expected_value)


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


def _extract_match_fact(evidence):
    packet = evidence.get("system_confirmation", {})
    origin_state = packet.get("origin_system", {}).get("reported_state")
    receiving_state = packet.get("receiving_system", {}).get("reported_state")
    if not isinstance(origin_state, str) or not origin_state:
        return {
            "name": "cross_system_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(receiving_state, str) or not receiving_state:
        return {
            "name": "cross_system_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    return {
        "name": "cross_system_state_match",
        "value": origin_state == receiving_state,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(match_fact, expected_value):
    actual = match_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [match_fact],
            "reason": (
                f"cross_system_state_match is {actual}, which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [match_fact],
        "reason": (
            f"cross_system_state_match is {actual}, which does not match the expected value {expected_value}."
        ),
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
