def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    coverage_evaluation = evaluation_index.get("coverage")
    branch_evaluation = evaluation_index.get("branch_coverage")
    if coverage_evaluation is None or branch_evaluation is None:
        return _build_inconclusive_result(
            "This test requires both coverage and branch_coverage evaluations with minimum criteria."
        )

    coverage_minimum = _read_numeric_criterion(coverage_evaluation, "minimum")
    branch_minimum = _read_numeric_criterion(branch_evaluation, "minimum")
    if coverage_minimum is None or branch_minimum is None:
        return _build_inconclusive_result(
            "This test requires coverage and branch_coverage criteria.minimum values to be numeric."
        )

    coverage_fact = _extract_measure_fact(evidence, "coverage")
    if coverage_fact["status"] != "found":
        return _build_inconclusive_result(
            [coverage_fact],
            "Unable to evaluate because the coverage fact could not be established.",
        )

    branch_fact = _extract_measure_fact(evidence, "branch_coverage")
    if branch_fact["status"] != "found":
        return _build_inconclusive_result(
            [branch_fact],
            "Unable to evaluate because the branch_coverage fact could not be established.",
        )

    return _evaluate_dual_thresholds(
        coverage_fact,
        branch_fact,
        coverage_minimum,
        branch_minimum,
    )


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


def _evaluate_dual_thresholds(coverage_fact, branch_fact, coverage_minimum, branch_minimum):
    failures = []
    if coverage_fact["value"] < coverage_minimum:
        failures.append(f"coverage is below {coverage_minimum}%")
    if branch_fact["value"] < branch_minimum:
        failures.append(f"branch_coverage is below {branch_minimum}%")

    if not failures:
        return {
            "conclusion": "true",
            "facts": [coverage_fact, branch_fact],
            "reason": (
                f"Coverage is {coverage_fact['value']}% and branch_coverage is "
                f"{branch_fact['value']}%, which both meet their required minimums."
            ),
        }

    return {
        "conclusion": "false",
        "facts": [coverage_fact, branch_fact],
        "reason": " and ".join(failures) + ".",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
