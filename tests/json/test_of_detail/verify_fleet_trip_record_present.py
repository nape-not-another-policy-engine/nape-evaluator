def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    trip_evaluation = evaluation_index.get("trip_record_present")
    if trip_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a trip_record_present evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(trip_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires trip_record_present criteria.equals to be boolean."
        )

    trip_fact = _extract_trip_present_fact(evidence)
    if trip_fact["status"] != "found":
        return _build_inconclusive_result(
            [trip_fact],
            "Unable to evaluate because the trip_record_present fact could not be established.",
        )

    return _evaluate_equals(trip_fact, expected_value)


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


def _extract_trip_present_fact(evidence):
    value = evidence.get("fleet_telematics", {}).get("trip_record", {}).get("trip_id")
    return {
        "name": "trip_record_present",
        "value": value not in (None, ""),
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(trip_fact, expected_value):
    actual = trip_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [trip_fact],
            "reason": f"trip_record_present is {actual}, which matches the expected value.",
        }
    return {
        "conclusion": "false",
        "facts": [trip_fact],
        "reason": f"trip_record_present is {actual}, which does not match the expected value {expected_value}.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
