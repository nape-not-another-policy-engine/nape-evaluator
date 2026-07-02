from datetime import date


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    review_evaluation = evaluation_index.get("review_date")
    if review_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a review_date evaluation with minimum and maximum criteria."
        )

    minimum = _read_date_criterion(review_evaluation, "minimum")
    maximum = _read_date_criterion(review_evaluation, "maximum")
    if minimum is None or maximum is None:
        return _build_inconclusive_result(
            "This test requires review_date criteria.minimum and criteria.maximum to be ISO-8601 dates."
        )

    review_fact = _extract_review_date_fact(evidence)
    if review_fact["status"] != "found":
        return _build_inconclusive_result(
            [_public_fact(review_fact)],
            "Unable to evaluate because the review_date fact could not be established.",
        )

    return _evaluate_range(review_fact, minimum, maximum)


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


def _read_date_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if not isinstance(value, str) or not value:
        return None
    return _parse_iso_date(value)


def _extract_review_date_fact(evidence):
    raw_value = evidence.get("backup_review", {}).get("review_date")
    if raw_value in (None, ""):
        return {
            "name": "review_date",
            "value": None,
            "value_type": "date",
            "status": "not_found",
        }

    parsed_value = _parse_iso_date(raw_value)
    if parsed_value is None:
        return {
            "name": "review_date",
            "value": raw_value,
            "value_type": "date",
            "status": "invalid",
        }

    return {
        "name": "review_date",
        "value": raw_value,
        "value_type": "date",
        "status": "found",
        "parsed_value": parsed_value,
    }


def _evaluate_range(review_fact, minimum, maximum):
    actual = review_fact["parsed_value"]
    if minimum <= actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [_public_fact(review_fact)],
            "reason": (
                f"review_date is {review_fact['value']}, which is within the allowed "
                f"range of {minimum.isoformat()} to {maximum.isoformat()}."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [_public_fact(review_fact)],
        "reason": (
            f"review_date is {review_fact['value']}, which is outside the allowed "
            f"range of {minimum.isoformat()} to {maximum.isoformat()}."
        ),
    }


def _parse_iso_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _public_fact(review_fact):
    return {
        "name": review_fact["name"],
        "value": review_fact["value"],
        "value_type": review_fact["value_type"],
        "status": review_fact["status"],
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
