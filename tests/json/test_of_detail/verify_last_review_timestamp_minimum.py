from datetime import datetime


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    timestamp_evaluation = evaluation_index.get("last_review_timestamp")
    if timestamp_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a last_review_timestamp evaluation with a minimum criterion."
        )

    minimum_timestamp = _read_minimum_datetime(timestamp_evaluation)
    if minimum_timestamp is None:
        return _build_inconclusive_result(
            "This test requires last_review_timestamp criteria.minimum to be an ISO-8601 datetime string."
        )

    timestamp_fact = _extract_review_timestamp_fact(evidence)
    if timestamp_fact["status"] != "found":
        return _build_inconclusive_result(
            [timestamp_fact],
            "Unable to evaluate because the last_review_timestamp fact could not be established.",
        )

    return _evaluate_minimum_timestamp(timestamp_fact, minimum_timestamp)


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_inconclusive_result("This test expects JSON evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result("This test only supports evaluator schema version 2.")
    if not isinstance(evidence, dict):
        return _build_inconclusive_result("This test expects JSON evidence as a dictionary.")
    return None


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item.get("subject", {})
        name = subject.get("name")
        if isinstance(name, str):
            indexed[name] = item
    return indexed


def _read_minimum_datetime(evaluation):
    value = evaluation.get("criteria", {}).get("minimum")
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


def _evaluate_minimum_timestamp(timestamp_fact, minimum_timestamp):
    actual_timestamp = timestamp_fact["parsed_value"]
    if actual_timestamp >= minimum_timestamp:
        return {
            "conclusion": "true",
            "facts": [_public_fact(timestamp_fact)],
            "reason": (
                f"last_review_timestamp is {timestamp_fact['value']}, which meets the "
                "required minimum datetime."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [_public_fact(timestamp_fact)],
        "reason": (
            f"last_review_timestamp is {timestamp_fact['value']}, which is older than the "
            "required minimum datetime."
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


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    public_facts = [_public_fact(fact) if "parsed_value" in fact else fact for fact in facts]
    return {
        "conclusion": "inconclusive",
        "facts": public_facts,
        "reason": reason,
    }
