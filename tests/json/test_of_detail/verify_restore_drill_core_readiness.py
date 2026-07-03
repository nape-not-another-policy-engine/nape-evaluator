from datetime import datetime


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_status = _read_expected_status(evaluation_index.get("restore_drill_status"))
    maximum_duration = _read_duration_criterion(
        evaluation_index.get("restore_drill_duration"),
        "maximum",
    )
    minimum_timestamp = _read_minimum_datetime(
        evaluation_index.get("restore_drill_timestamp")
    )

    if expected_status is None or maximum_duration is None or minimum_timestamp is None:
        return _build_inconclusive_result(
            "This test requires restore_drill_status equals, restore_drill_duration maximum, and restore_drill_timestamp minimum."
        )

    status_fact = _extract_status_fact(evidence)
    duration_fact = _extract_restore_duration_fact(evidence)
    timestamp_fact = _extract_restore_timestamp_fact(evidence)
    facts = [status_fact, _public_duration_fact(duration_fact), _public_timestamp_fact(timestamp_fact)]

    failed_establishment = []
    for fact in (status_fact, duration_fact, timestamp_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate restore readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if status_fact["value"] != expected_status:
        conclusion = "false"
        reasons.append(
            f"restore_drill_status is '{status_fact['value']}', not '{expected_status}'."
        )

    if duration_fact["parsed_seconds"] > maximum_duration:
        conclusion = "false"
        reasons.append(
            f"restore_drill_duration is {duration_fact['value']}, which exceeds the allowed maximum duration."
        )

    if timestamp_fact["parsed_value"] < minimum_timestamp:
        conclusion = "false"
        reasons.append(
            f"restore_drill_timestamp is {timestamp_fact['value']}, which is older than the required minimum datetime."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Restore readiness controls are satisfied: the drill completed successfully, "
                "the duration stayed within threshold, and the drill is recent enough."
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


def _read_duration_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if not isinstance(value, str) or not value:
        return None
    return _parse_duration_seconds(value)


def _read_minimum_datetime(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("minimum")
    if not isinstance(value, str) or not value:
        return None
    return _parse_utc_datetime(value)


def _extract_status_fact(evidence):
    value = evidence.get("restore_drill", {}).get("restore_drill_status")
    return {
        "name": "restore_drill_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_restore_duration_fact(evidence):
    raw_value = evidence.get("restore_drill", {}).get("restore_drill_duration")
    if raw_value in (None, ""):
        return {
            "name": "restore_drill_duration",
            "value": None,
            "value_type": "duration",
            "status": "not_found",
        }
    parsed_seconds = _parse_duration_seconds(raw_value)
    if parsed_seconds is None:
        return {
            "name": "restore_drill_duration",
            "value": raw_value,
            "value_type": "duration",
            "status": "invalid",
        }
    return {
        "name": "restore_drill_duration",
        "value": raw_value,
        "value_type": "duration",
        "status": "found",
        "parsed_seconds": parsed_seconds,
    }


def _extract_restore_timestamp_fact(evidence):
    raw_value = evidence.get("restore_drill", {}).get("restore_drill_timestamp")
    if raw_value in (None, ""):
        return {
            "name": "restore_drill_timestamp",
            "value": None,
            "value_type": "datetime",
            "status": "not_found",
        }
    parsed_value = _parse_utc_datetime(raw_value)
    if parsed_value is None:
        return {
            "name": "restore_drill_timestamp",
            "value": raw_value,
            "value_type": "datetime",
            "status": "invalid",
        }
    return {
        "name": "restore_drill_timestamp",
        "value": raw_value,
        "value_type": "datetime",
        "status": "found",
        "parsed_value": parsed_value,
    }


def _parse_duration_seconds(value):
    if not value.startswith("PT"):
        return None
    remainder = value[2:]
    if not remainder:
        return None
    total = 0
    number = ""
    unit_seconds = {"H": 3600, "M": 60, "S": 1}
    seen_unit = False
    for char in remainder:
        if char.isdigit():
            number += char
            continue
        if char not in unit_seconds or not number:
            return None
        total += int(number) * unit_seconds[char]
        number = ""
        seen_unit = True
    if number or not seen_unit:
        return None
    return total


def _parse_utc_datetime(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _public_duration_fact(duration_fact):
    return {
        "name": duration_fact["name"],
        "value": duration_fact["value"],
        "value_type": duration_fact["value_type"],
        "status": duration_fact["status"],
    }


def _public_timestamp_fact(timestamp_fact):
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
