def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    coverage_evaluation = evaluation_index.get("coverage")
    if coverage_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a coverage evaluation with a minimum criterion."
        )

    minimum = _read_numeric_criterion(coverage_evaluation, "minimum")
    if minimum is None:
        return _build_inconclusive_result(
            "This test requires coverage criteria.minimum to be numeric."
        )

    coverage_fact = _extract_measure_fact(evidence, "coverage")
    if coverage_fact["status"] != "found":
        return _build_inconclusive_result(
            [coverage_fact],
            "The YAML coverage fact was present but invalid for numeric evaluation, so the conclusion is inconclusive.",
        )

    return _evaluate_minimum(coverage_fact, minimum)


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "yaml":
        return _build_inconclusive_result("This test expects YAML evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result(
            "This test only supports evaluator schema version 2."
        )
    if not isinstance(evidence, dict):
        return _build_inconclusive_result(
            "This test expects YAML evidence as a dictionary."
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


def _evaluate_minimum(coverage_fact, minimum):
    actual = coverage_fact["value"]
    if actual >= minimum:
        return {
            "conclusion": "true",
            "facts": [coverage_fact],
            "reason": f"Coverage is {actual}%, which meets the required minimum of {minimum}%.",
        }
    return {
        "conclusion": "false",
        "facts": [coverage_fact],
        "reason": f"Coverage is {actual}%, which is below the required minimum of {minimum}%.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
