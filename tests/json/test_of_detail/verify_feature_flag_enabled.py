def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    feature_evaluation = evaluation_index.get("feature_enabled")
    if feature_evaluation is None:
        return _build_error_result(
            "This test requires a feature_enabled evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(feature_evaluation)
    if expected_value is None:
        return _build_error_result(
            "This test requires feature_enabled criteria.equals to be boolean."
        )

    feature_fact = _extract_feature_flag_fact(evidence)
    if feature_fact["status"] != "found":
        return _build_inconclusive_result(
            [feature_fact],
            "Unable to evaluate because the feature_enabled fact could not be established.",
        )

    return _evaluate_equals(feature_fact, expected_value)


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


def _read_boolean_equals(evaluation):
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_feature_flag_fact(evidence):
    value = evidence.get("component", {}).get("feature_enabled")
    if value is None:
        return {
            "name": "feature_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "feature_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "feature_enabled",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(feature_fact, expected_value):
    actual = feature_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [feature_fact],
            "reason": f"feature_enabled is {actual}, which matches the expected value.",
        }
    return {
        "conclusion": "false",
        "facts": [feature_fact],
        "reason": f"feature_enabled is {actual}, which does not match the expected value {expected_value}.",
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
