def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    calibration_evaluation = evaluation_index.get("calibration_current")
    if calibration_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a calibration_current evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(calibration_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires calibration_current criteria.equals to be boolean."
        )

    calibration_fact = _extract_calibration_fact(evidence)
    if calibration_fact["status"] != "found":
        return _build_inconclusive_result(
            [calibration_fact],
            "Unable to evaluate because the calibration_current fact could not be established.",
        )

    return _evaluate_equals(calibration_fact, expected_value)


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


def _extract_calibration_fact(evidence):
    value = evidence.get("return_to_service", {}).get("calibration_current")
    if value is None:
        return {
            "name": "calibration_current",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "calibration_current",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "calibration_current",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(calibration_fact, expected_value):
    actual = calibration_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [calibration_fact],
            "reason": (
                f"calibration_current is {actual}, which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [calibration_fact],
        "reason": (
            f"calibration_current is {actual}, which does not match the expected value {expected_value}."
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
