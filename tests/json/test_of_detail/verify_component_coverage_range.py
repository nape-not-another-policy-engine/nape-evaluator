def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    coverage_evaluation = evaluation_index.get("coverage")
    if coverage_evaluation is None:
        return _build_error_result(
            "This test requires a coverage evaluation with minimum and maximum criteria."
        )

    minimum = _read_numeric_criterion(coverage_evaluation, "minimum")
    maximum = _read_numeric_criterion(coverage_evaluation, "maximum")
    if minimum is None or maximum is None:
        return _build_error_result(
            "This test requires coverage criteria.minimum and criteria.maximum to be numeric."
        )

    coverage_fact = _extract_measure_fact(evidence, "coverage")
    if coverage_fact["status"] != "found":
        return _build_inconclusive_result(
            [coverage_fact],
            "Unable to evaluate because the coverage fact could not be established.",
        )

    return _evaluate_range(coverage_fact, minimum, maximum)


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


def _read_numeric_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _extract_measure_fact(evidence, metric_name):
    measures = evidence.get("component", {}).get("measures", [])
    for measure in measures:
        if measure.get("metric") != metric_name:
            continue
        value = measure.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return {
                "name": metric_name,
                "value": None,
                "value_type": "number",
                "unit": "percent",
                "status": "invalid",
            }
        return {
            "name": metric_name,
            "value": float(value),
            "value_type": "number",
            "unit": "percent",
            "status": "found",
        }

    return {
        "name": metric_name,
        "value": None,
        "value_type": "number",
        "unit": "percent",
        "status": "not_found",
    }


def _evaluate_range(coverage_fact, minimum, maximum):
    actual = coverage_fact["value"]
    if minimum <= actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [coverage_fact],
            "reason": f"Coverage is {actual}%, which is within the allowed range of {minimum}% to {maximum}%.",
        }
    return {
        "conclusion": "false",
        "facts": [coverage_fact],
        "reason": f"Coverage is {actual}%, which is outside the allowed range of {minimum}% to {maximum}%.",
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
