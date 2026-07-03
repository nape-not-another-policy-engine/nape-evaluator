def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_trip = _read_boolean_equals(evaluation_index.get("trip_record_present"))
    expected_vehicle_match = _read_boolean_equals(
        evaluation_index.get("telematics_vehicle_match")
    )
    expected_state_match = _read_boolean_equals(
        evaluation_index.get("telematics_state_match")
    )

    if (
        expected_trip is None
        or expected_vehicle_match is None
        or expected_state_match is None
    ):
        return _build_inconclusive_result(
            "This test requires trip_record_present equals, telematics_vehicle_match equals, and telematics_state_match equals."
        )

    trip_fact = _extract_trip_present_fact(evidence)
    vehicle_fact = _extract_vehicle_match_fact(evidence)
    state_fact = _extract_state_match_fact(evidence)
    facts = [trip_fact, vehicle_fact, state_fact]

    failed_establishment = []
    for fact in (trip_fact, vehicle_fact, state_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate fleet telematics reconciliation because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if trip_fact["value"] != expected_trip:
        conclusion = "false"
        reasons.append(
            f"trip_record_present is {trip_fact['value']}, not {expected_trip}."
        )

    if vehicle_fact["value"] != expected_vehicle_match:
        conclusion = "false"
        reasons.append(
            f"telematics_vehicle_match is {vehicle_fact['value']}, not {expected_vehicle_match}."
        )

    if state_fact["value"] != expected_state_match:
        conclusion = "false"
        reasons.append(
            f"telematics_state_match is {state_fact['value']}, not {expected_state_match}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Fleet telematics reconciliation is satisfied: the trip record is present, "
                "vehicle identity matches, and reported state matches."
            ),
        }

    return {
        "conclusion": "false",
        "facts": facts,
        "reason": " ".join(reasons),
    }


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
    if not isinstance(evaluation, dict):
        return None
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


def _extract_vehicle_match_fact(evidence):
    packet = evidence.get("fleet_telematics", {})
    trip_vehicle = packet.get("trip_record", {}).get("vehicle_identifier")
    telematics_vehicle = packet.get("telematics", {}).get("vehicle_identifier")
    if not isinstance(trip_vehicle, str) or not trip_vehicle:
        return {
            "name": "telematics_vehicle_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(telematics_vehicle, str) or not telematics_vehicle:
        return {
            "name": "telematics_vehicle_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    return {
        "name": "telematics_vehicle_match",
        "value": trip_vehicle == telematics_vehicle,
        "value_type": "boolean",
        "status": "found",
    }


def _extract_state_match_fact(evidence):
    packet = evidence.get("fleet_telematics", {})
    trip_state = packet.get("trip_record", {}).get("reported_state")
    telematics_state = packet.get("telematics", {}).get("reported_state")
    if not isinstance(trip_state, str) or not trip_state:
        return {
            "name": "telematics_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(telematics_state, str) or not telematics_state:
        return {
            "name": "telematics_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    return {
        "name": "telematics_state_match",
        "value": trip_state == telematics_state,
        "value_type": "boolean",
        "status": "found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
