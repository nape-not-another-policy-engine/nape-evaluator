from datetime import datetime


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)

    status_expected = _read_expected_status(
        evaluation_index.get("access_request_status")
    )
    approver_required = _read_required(
        evaluation_index.get("approver_identifier")
    )
    review_minimum = _read_minimum_datetime(
        evaluation_index.get("last_review_timestamp")
    )

    if status_expected is None or approver_required is not True or review_minimum is None:
        return _build_inconclusive_result(
            "This test requires access_request_status equals, approver_identifier required=true, and last_review_timestamp minimum."
        )

    status_fact = _extract_status_fact(evidence)
    approver_fact = _extract_approver_fact(evidence)
    timestamp_fact = _extract_review_timestamp_fact(evidence)
    facts = [status_fact, approver_fact, _public_fact(timestamp_fact)]

    failed_establishment = []
    for fact in (status_fact, approver_fact, timestamp_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate privileged access core controls because these facts "
                f"could not be established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if status_fact["value"] != status_expected:
        conclusion = "false"
        reasons.append(
            f"access_request_status is '{status_fact['value']}', not '{status_expected}'."
        )

    if timestamp_fact["parsed_value"] < review_minimum:
        conclusion = "false"
        reasons.append(
            f"last_review_timestamp is {timestamp_fact['value']}, which is older than the required minimum datetime."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Privileged access core controls are satisfied: the request is approved, "
                "an approver identifier is present, and the review is recent enough."
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


def _read_required(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("required")
    return value if isinstance(value, bool) else None


def _read_minimum_datetime(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("minimum")
    if not isinstance(value, str) or not value:
        return None
    return _parse_utc_datetime(value)


def _extract_status_fact(evidence):
    value = evidence.get("privileged_access_review", {}).get("request_status")
    return {
        "name": "access_request_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_approver_fact(evidence):
    value = evidence.get("privileged_access_review", {}).get("approver_identifier")
    return {
        "name": "approver_identifier",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_review_timestamp_fact(evidence):
    raw_value = evidence.get("privileged_access_review", {}).get("last_review_timestamp")
    if raw_value in (None, ""):
        return {
            "name": "last_review_timestamp",
            "value": None,
            "value_type": "datetime",
            "status": "not_found",
        }
    parsed_value = _parse_utc_datetime(raw_value)
    if parsed_value is None:
        return {
            "name": "last_review_timestamp",
            "value": raw_value,
            "value_type": "datetime",
            "status": "invalid",
        }
    return {
        "name": "last_review_timestamp",
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
