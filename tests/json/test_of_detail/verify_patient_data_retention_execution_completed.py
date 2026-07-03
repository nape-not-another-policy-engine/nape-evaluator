def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    retention_evaluation = evaluation_index.get("retention_execution_status")
    if retention_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a retention_execution_status evaluation with an equals criterion."
        )

    expected_value = _read_expected_status(retention_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires retention_execution_status criteria.equals to be non-empty text."
        )

    retention_fact = _extract_retention_fact(evidence)
    if retention_fact["status"] != "found":
        return _build_inconclusive_result(
            [retention_fact],
            "Unable to evaluate because the retention_execution_status fact could not be established.",
        )

    return _evaluate_equals(retention_fact, expected_value)


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


def _read_expected_status(evaluation):
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _extract_retention_fact(evidence):
    value = evidence.get("patient_data_export", {}).get("retention_execution_status")
    return {
        "name": "retention_execution_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _evaluate_equals(retention_fact, expected_value):
    actual = retention_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [retention_fact],
            "reason": (
                f"retention_execution_status is '{actual}', which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [retention_fact],
        "reason": (
            f"retention_execution_status is '{actual}', which does not match the expected value '{expected_value}'."
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
