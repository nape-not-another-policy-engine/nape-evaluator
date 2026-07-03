def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_release = _read_expected_status(
        evaluation_index.get("maintenance_release_status")
    )
    expected_hazard = _read_expected_status(
        evaluation_index.get("hazard_closure_status")
    )
    expected_calibration = _read_boolean_equals(
        evaluation_index.get("calibration_current")
    )

    if (
        expected_release is None
        or expected_hazard is None
        or expected_calibration is None
    ):
        return _build_inconclusive_result(
            "This test requires maintenance_release_status equals, hazard_closure_status equals, and calibration_current equals."
        )

    release_fact = _extract_release_fact(evidence)
    hazard_fact = _extract_hazard_fact(evidence)
    calibration_fact = _extract_calibration_fact(evidence)
    facts = [release_fact, hazard_fact, calibration_fact]

    failed_establishment = []
    for fact in (release_fact, hazard_fact, calibration_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate return-to-service readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if release_fact["value"] != expected_release:
        conclusion = "false"
        reasons.append(
            f"maintenance_release_status is '{release_fact['value']}', not '{expected_release}'."
        )

    if hazard_fact["value"] != expected_hazard:
        conclusion = "false"
        reasons.append(
            f"hazard_closure_status is '{hazard_fact['value']}', not '{expected_hazard}'."
        )

    if calibration_fact["value"] != expected_calibration:
        conclusion = "false"
        reasons.append(
            f"calibration_current is {calibration_fact['value']}, not {expected_calibration}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Return-to-service readiness is satisfied: maintenance release is approved, "
                "hazards are closed, and calibration is current."
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


def _read_expected_status(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _read_boolean_equals(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_release_fact(evidence):
    value = evidence.get("return_to_service", {}).get("maintenance_release_status")
    return {
        "name": "maintenance_release_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_hazard_fact(evidence):
    value = evidence.get("return_to_service", {}).get("hazard_closure_status")
    return {
        "name": "hazard_closure_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


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


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
