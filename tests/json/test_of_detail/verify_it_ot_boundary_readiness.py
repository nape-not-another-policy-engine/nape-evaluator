def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_remote_access = _read_boolean_equals(
        evaluation_index.get("remote_access_enabled")
    )
    maximum_exposed = _read_integer_criterion(
        evaluation_index.get("internet_exposed_controller_count"), "maximum"
    )
    expected_boundary_status = _read_expected_status(
        evaluation_index.get("boundary_control_status")
    )

    if (
        expected_remote_access is None
        or maximum_exposed is None
        or expected_boundary_status is None
    ):
        return _build_inconclusive_result(
            "This test requires remote_access_enabled equals, internet_exposed_controller_count maximum, and boundary_control_status equals."
        )

    remote_access_fact = _extract_remote_access_fact(evidence)
    exposure_fact = _extract_count_fact(evidence)
    boundary_fact = _extract_status_fact(evidence)
    facts = [remote_access_fact, exposure_fact, boundary_fact]

    failed_establishment = []
    for fact in (remote_access_fact, exposure_fact, boundary_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate IT / OT boundary readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if remote_access_fact["value"] != expected_remote_access:
        conclusion = "false"
        reasons.append(
            f"remote_access_enabled is {remote_access_fact['value']}, not {expected_remote_access}."
        )

    if exposure_fact["value"] > maximum_exposed:
        conclusion = "false"
        reasons.append(
            "internet_exposed_controller_count is "
            f"{exposure_fact['value']}, which exceeds the allowed maximum of {maximum_exposed}."
        )

    if boundary_fact["value"] != expected_boundary_status:
        conclusion = "false"
        reasons.append(
            f"boundary_control_status is '{boundary_fact['value']}', not '{expected_boundary_status}'."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "IT / OT boundary readiness is satisfied: remote access state matches expectation, "
                "no disallowed controller exposure is present, and the boundary control status is segmented."
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


def _read_integer_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _read_expected_status(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _extract_remote_access_fact(evidence):
    value = evidence.get("it_ot_boundary", {}).get("remote_access_enabled")
    if value is None:
        return {
            "name": "remote_access_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "remote_access_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "remote_access_enabled",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _extract_count_fact(evidence):
    value = evidence.get("it_ot_boundary", {}).get(
        "internet_exposed_controller_count"
    )
    if value is None:
        return {
            "name": "internet_exposed_controller_count",
            "value": None,
            "value_type": "integer",
            "status": "not_found",
        }
    if not isinstance(value, int) or isinstance(value, bool):
        return {
            "name": "internet_exposed_controller_count",
            "value": None,
            "value_type": "integer",
            "status": "invalid",
        }
    return {
        "name": "internet_exposed_controller_count",
        "value": value,
        "value_type": "integer",
        "status": "found",
    }


def _extract_status_fact(evidence):
    value = evidence.get("it_ot_boundary", {}).get("boundary_control_status")
    return {
        "name": "boundary_control_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
