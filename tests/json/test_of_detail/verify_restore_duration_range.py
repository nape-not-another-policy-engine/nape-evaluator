def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    duration_evaluation = evaluation_index.get("restore_duration")
    if duration_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a restore_duration evaluation with minimum and maximum criteria."
        )

    minimum = _read_duration_criterion(duration_evaluation, "minimum")
    maximum = _read_duration_criterion(duration_evaluation, "maximum")
    if minimum is None or maximum is None:
        return _build_inconclusive_result(
            "This test requires restore_duration criteria.minimum and criteria.maximum to be supported ISO-8601 durations."
        )

    duration_fact = _extract_restore_duration_fact(evidence)
    if duration_fact["status"] != "found":
        return _build_inconclusive_result(
            [_public_fact(duration_fact)],
            "Unable to evaluate because the restore_duration fact could not be established.",
        )

    return _evaluate_range(duration_fact, minimum, maximum)


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


def _read_duration_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if not isinstance(value, str) or not value:
        return None
    return _parse_duration_seconds(value)


def _extract_restore_duration_fact(evidence):
    raw_value = evidence.get("backup_review", {}).get("restore_duration")
    if raw_value in (None, ""):
        return {
            "name": "restore_duration",
            "value": None,
            "value_type": "duration",
            "status": "not_found",
        }

    parsed_seconds = _parse_duration_seconds(raw_value)
    if parsed_seconds is None:
        return {
            "name": "restore_duration",
            "value": raw_value,
            "value_type": "duration",
            "status": "invalid",
        }

    return {
        "name": "restore_duration",
        "value": raw_value,
        "value_type": "duration",
        "status": "found",
        "parsed_seconds": parsed_seconds,
    }


def _evaluate_range(duration_fact, minimum, maximum):
    actual = duration_fact["parsed_seconds"]
    if minimum <= actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [_public_fact(duration_fact)],
            "reason": (
                f"restore_duration is {duration_fact['value']}, which is within the allowed "
                "duration range."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [_public_fact(duration_fact)],
        "reason": (
            f"restore_duration is {duration_fact['value']}, which is outside the allowed "
            "duration range."
        ),
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


def _public_fact(duration_fact):
    return {
        "name": duration_fact["name"],
        "value": duration_fact["value"],
        "value_type": duration_fact["value_type"],
        "status": duration_fact["status"],
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
