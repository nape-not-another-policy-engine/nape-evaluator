from datetime import datetime


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    timestamp_evaluation = evaluation_index.get("last_review_timestamp")
    if timestamp_evaluation is None:
        return _build_error_result(
            "This test requires a last_review_timestamp evaluation with minimum and maximum criteria."
        )

    minimum_timestamp = _read_datetime_criterion(timestamp_evaluation, "minimum")
    maximum_timestamp = _read_datetime_criterion(timestamp_evaluation, "maximum")
    if minimum_timestamp is None or maximum_timestamp is None:
        return _build_error_result(
            "This test requires last_review_timestamp criteria.minimum and criteria.maximum to be ISO-8601 datetime strings."
        )

    timestamp_fact = _extract_review_timestamp_fact(evidence)
    if timestamp_fact["status"] != "found":
        return _build_inconclusive_result(
            [_public_fact(timestamp_fact)],
            "Unable to evaluate because the last_review_timestamp fact could not be established.",
        )

    return _evaluate_range(timestamp_fact, minimum_timestamp, maximum_timestamp)


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


def _read_datetime_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if not isinstance(value, str) or not value:
        return None
    return _parse_utc_datetime(value)


def _extract_review_timestamp_fact(evidence):
    raw_value = evidence.get("access_review", {}).get("last_review_timestamp")
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


def _evaluate_range(timestamp_fact, minimum_timestamp, maximum_timestamp):
    actual = timestamp_fact["parsed_value"]
    if minimum_timestamp <= actual <= maximum_timestamp:
        return {
            "conclusion": "true",
            "facts": [_public_fact(timestamp_fact)],
            "reason": (
                f"last_review_timestamp is {timestamp_fact['value']}, which is within the "
                "allowed datetime range."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [_public_fact(timestamp_fact)],
        "reason": (
            f"last_review_timestamp is {timestamp_fact['value']}, which is outside the "
            "allowed datetime range."
        ),
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
