def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    count_evaluation = evaluation_index.get("temperature_excursion_count")
    if count_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a temperature_excursion_count evaluation with a maximum criterion."
        )

    maximum = _read_integer_criterion(count_evaluation, "maximum")
    if maximum is None:
        return _build_inconclusive_result(
            "This test requires temperature_excursion_count criteria.maximum to be an integer."
        )

    count_fact = _extract_count_fact(evidence)
    if count_fact["status"] != "found":
        return _build_inconclusive_result(
            [count_fact],
            "Unable to evaluate because the temperature_excursion_count fact could not be established.",
        )

    return _evaluate_maximum(count_fact, maximum)


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


def _read_integer_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _extract_count_fact(evidence):
    value = evidence.get("cold_chain_exception", {}).get("temperature_excursion_count")
    if value is None:
        return {
            "name": "temperature_excursion_count",
            "value": None,
            "value_type": "integer",
            "status": "not_found",
        }
    if not isinstance(value, int) or isinstance(value, bool):
        return {
            "name": "temperature_excursion_count",
            "value": None,
            "value_type": "integer",
            "status": "invalid",
        }
    return {
        "name": "temperature_excursion_count",
        "value": value,
        "value_type": "integer",
        "status": "found",
    }


def _evaluate_maximum(count_fact, maximum):
    actual = count_fact["value"]
    if actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [count_fact],
            "reason": (
                f"temperature_excursion_count is {actual}, which is within the allowed maximum of {maximum}."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [count_fact],
        "reason": (
            f"temperature_excursion_count is {actual}, which exceeds the allowed maximum of {maximum}."
        ),
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
