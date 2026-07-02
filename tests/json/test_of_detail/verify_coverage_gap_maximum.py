def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    gap_evaluation = evaluation_index.get("coverage_gap")
    if gap_evaluation is None:
        return _build_error_result(
            "This test requires a coverage_gap evaluation with a maximum criterion."
        )

    maximum = _read_numeric_criterion(gap_evaluation, "maximum")
    if maximum is None:
        return _build_error_result(
            "This test requires coverage_gap criteria.maximum to be numeric."
        )

    coverage_fact = _extract_measure_fact(evidence, "coverage")
    branch_fact = _extract_measure_fact(evidence, "branch_coverage")
    gap_fact = _derive_coverage_gap_fact(coverage_fact, branch_fact)
    if gap_fact["status"] != "found":
        return _build_inconclusive_result(
            [
                _public_fact(coverage_fact),
                _public_fact(branch_fact),
                _public_fact(gap_fact),
            ],
            "Unable to evaluate because the derived coverage_gap fact could not be established.",
        )

    return _evaluate_gap(coverage_fact, branch_fact, gap_fact, maximum)


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


def _derive_coverage_gap_fact(coverage_fact, branch_fact):
    statuses = {coverage_fact["status"], branch_fact["status"]}
    if "invalid" in statuses:
        return {
            "name": "coverage_gap",
            "value": None,
            "value_type": "number",
            "unit": "percentage_points",
            "status": "invalid",
        }
    if "not_found" in statuses:
        return {
            "name": "coverage_gap",
            "value": None,
            "value_type": "number",
            "unit": "percentage_points",
            "status": "not_found",
        }

    return {
        "name": "coverage_gap",
        "value": abs(branch_fact["value"] - coverage_fact["value"]),
        "value_type": "number",
        "unit": "percentage_points",
        "status": "found",
    }


def _evaluate_gap(coverage_fact, branch_fact, gap_fact, maximum):
    actual_gap = gap_fact["value"]
    if actual_gap <= maximum:
        return {
            "conclusion": "true",
            "facts": [
                _public_fact(coverage_fact),
                _public_fact(branch_fact),
                _public_fact(gap_fact),
            ],
            "reason": (
                f"coverage_gap is {actual_gap} percentage points, derived from coverage "
                f"{coverage_fact['value']}% and branch_coverage {branch_fact['value']}%, "
                f"which is within the allowed maximum of {maximum}."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [
            _public_fact(coverage_fact),
            _public_fact(branch_fact),
            _public_fact(gap_fact),
        ],
        "reason": (
            f"coverage_gap is {actual_gap} percentage points, derived from coverage "
            f"{coverage_fact['value']}% and branch_coverage {branch_fact['value']}%, "
            f"which exceeds the allowed maximum of {maximum}."
        ),
    }


def _public_fact(fact):
    public_fact = {
        "name": fact["name"],
        "value": fact["value"],
        "value_type": fact["value_type"],
        "status": fact["status"],
    }
    if "unit" in fact:
        public_fact["unit"] = fact["unit"]
    return public_fact


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
