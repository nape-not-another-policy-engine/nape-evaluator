def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    approval_evaluation = evaluation_index.get("interconnection_approval_present")
    if approval_evaluation is None:
        return _build_inconclusive_result(
            "This test requires an interconnection_approval_present evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(approval_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires interconnection_approval_present criteria.equals to be boolean."
        )

    approval_fact = _extract_approval_fact(evidence)
    if approval_fact["status"] != "found":
        return _build_inconclusive_result(
            [approval_fact],
            "Unable to evaluate because the interconnection_approval_present fact could not be established.",
        )

    return _evaluate_equals(approval_fact, expected_value)


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


def _extract_approval_fact(evidence):
    value = evidence.get("system_confirmation", {}).get("interconnection", {}).get(
        "approval_id"
    )
    return {
        "name": "interconnection_approval_present",
        "value": value not in (None, ""),
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(approval_fact, expected_value):
    actual = approval_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [approval_fact],
            "reason": (
                f"interconnection_approval_present is {actual}, which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [approval_fact],
        "reason": (
            f"interconnection_approval_present is {actual}, which does not match the expected value {expected_value}."
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
