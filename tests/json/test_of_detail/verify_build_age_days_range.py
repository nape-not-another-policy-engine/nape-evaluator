def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    age_evaluation = evaluation_index.get("build_age_days")
    if age_evaluation is None:
        return _build_error_result(
            "This test requires a build_age_days evaluation with minimum and maximum criteria."
        )

    minimum = _read_integer_criterion(age_evaluation, "minimum")
    maximum = _read_integer_criterion(age_evaluation, "maximum")
    if minimum is None or maximum is None:
        return _build_error_result(
            "This test requires build_age_days criteria.minimum and criteria.maximum to be integers."
        )

    age_fact = _extract_build_age_fact(evidence)
    if age_fact["status"] != "found":
        return _build_inconclusive_result(
            [age_fact],
            "Unable to evaluate because the build_age_days fact could not be established.",
        )

    return _evaluate_range(age_fact, minimum, maximum)


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


def _read_integer_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _extract_build_age_fact(evidence):
    value = evidence.get("component", {}).get("build_age_days")
    if value is None:
        return {
            "name": "build_age_days",
            "value": None,
            "value_type": "integer",
            "status": "not_found",
        }
    if not isinstance(value, int) or isinstance(value, bool):
        return {
            "name": "build_age_days",
            "value": None,
            "value_type": "integer",
            "status": "invalid",
        }
    return {
        "name": "build_age_days",
        "value": value,
        "value_type": "integer",
        "status": "found",
    }


def _evaluate_range(age_fact, minimum, maximum):
    actual = age_fact["value"]
    if minimum <= actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [age_fact],
            "reason": (
                f"build_age_days is {actual}, which is within the allowed range of "
                f"{minimum} to {maximum}."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [age_fact],
        "reason": (
            f"build_age_days is {actual}, which is outside the allowed range of "
            f"{minimum} to {maximum}."
        ),
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
