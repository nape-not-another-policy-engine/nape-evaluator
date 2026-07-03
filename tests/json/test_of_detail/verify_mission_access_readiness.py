from datetime import datetime


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_status = _read_expected_status(
        evaluation_index.get("mission_access_status")
    )
    expected_approval = _read_boolean_equals(
        evaluation_index.get("mission_access_approval_present")
    )
    minimum_review = _read_minimum_datetime(
        evaluation_index.get("mission_access_review_timestamp")
    )

    if expected_status is None or expected_approval is None or minimum_review is None:
        return _build_inconclusive_result(
            "This test requires mission_access_status equals, mission_access_approval_present equals, and mission_access_review_timestamp minimum."
        )

    status_fact = _extract_status_fact(evidence)
    approval_fact = _extract_approval_fact(evidence)
    review_fact = _extract_review_timestamp_fact(evidence)
    facts = [status_fact, approval_fact, _public_fact(review_fact)]

    failed_establishment = []
    for fact in (status_fact, approval_fact, review_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate mission access readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if status_fact["value"] != expected_status:
        conclusion = "false"
        reasons.append(
            f"mission_access_status is '{status_fact['value']}', not '{expected_status}'."
        )

    if approval_fact["value"] != expected_approval:
        conclusion = "false"
        reasons.append(
            f"mission_access_approval_present is {approval_fact['value']}, not {expected_approval}."
        )

    if review_fact["parsed_value"] < minimum_review:
        conclusion = "false"
        reasons.append(
            f"mission_access_review_timestamp is {review_fact['value']}, which is older than the required minimum datetime."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Mission access readiness is satisfied: the access status is authorized, approval is present, "
                "and the review is recent enough."
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


def _read_minimum_datetime(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("minimum")
    if not isinstance(value, str) or not value:
        return None
    return _parse_utc_datetime(value)


def _extract_status_fact(evidence):
    value = evidence.get("mission_access_review", {}).get("mission_access_status")
    return {
        "name": "mission_access_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_approval_fact(evidence):
    value = evidence.get("mission_access_review", {}).get(
        "mission_access_approval_present"
    )
    if value is None:
        return {
            "name": "mission_access_approval_present",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "mission_access_approval_present",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "mission_access_approval_present",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _extract_review_timestamp_fact(evidence):
    raw_value = evidence.get("mission_access_review", {}).get(
        "mission_access_review_timestamp"
    )
    if raw_value in (None, ""):
        return {
            "name": "mission_access_review_timestamp",
            "value": None,
            "value_type": "datetime",
            "status": "not_found",
        }
    parsed_value = _parse_utc_datetime(raw_value)
    if parsed_value is None:
        return {
            "name": "mission_access_review_timestamp",
            "value": raw_value,
            "value_type": "datetime",
            "status": "invalid",
        }
    return {
        "name": "mission_access_review_timestamp",
        "value": raw_value,
        "value_type": "datetime",
        "status": "found",
        "parsed_value": parsed_value,
    }


def _parse_utc_datetime(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _public_fact(timestamp_fact):
    return {
        "name": timestamp_fact["name"],
        "value": timestamp_fact["value"],
        "value_type": timestamp_fact["value_type"],
        "status": timestamp_fact["status"],
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
