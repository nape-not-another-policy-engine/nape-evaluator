"""V2 test-of-detail scaffold.

This template reflects the current V2 contract:

- def evaluate(evidence, evaluations, metadata)
- one combined structured result object
"""


def evaluate(evidence, evaluations, metadata):
    _validate_metadata(metadata)
    evaluation_index = _index_evaluations(evaluations)
    facts = _extract_facts(evidence, evaluation_index)

    missing_or_invalid = _find_missing_or_invalid_facts(facts, evaluation_index)
    if missing_or_invalid:
        return _build_inconclusive_result(
            facts=list(facts.values()),
            reason=_build_missing_fact_reason(missing_or_invalid),
        )

    return _evaluate_policy(facts, evaluation_index)


def _validate_metadata(metadata):
    if metadata.get("evidence_type") != "json":
        raise ValueError("This test expects JSON evidence.")

    if metadata.get("schema_version") != "2":
        raise ValueError("This test only supports evaluator schema version 2.")


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item["subject"]
        indexed[subject["name"]] = item
    return indexed


def _extract_facts(evidence, evaluation_index):
    facts = {}

    if "coverage" in evaluation_index:
        facts["coverage"] = _extract_numeric_measure(
            evidence=evidence,
            metric_name="coverage",
            fact_name="coverage",
            unit="percent",
        )

    if "branch_coverage" in evaluation_index:
        facts["branch_coverage"] = _extract_numeric_measure(
            evidence=evidence,
            metric_name="branch_coverage",
            fact_name="branch_coverage",
            unit="percent",
        )

    return facts


def _extract_numeric_measure(evidence, metric_name, fact_name, unit=None):
    measures = evidence.get("component", {}).get("measures", [])
    for measure in measures:
        if measure.get("metric") != metric_name:
            continue

        raw_value = measure.get("value")
        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError):
            return {
                "name": fact_name,
                "value": None,
                "value_type": "number",
                "unit": unit,
                "status": "invalid",
            }

        return {
            "name": fact_name,
            "value": numeric_value,
            "value_type": "number",
            "unit": unit,
            "status": "found",
        }

    return {
        "name": fact_name,
        "value": None,
        "value_type": "number",
        "unit": unit,
        "status": "not_found",
    }


def _find_missing_or_invalid_facts(facts, evaluation_index):
    problems = []
    for subject_name, evaluation in evaluation_index.items():
        criteria = evaluation["criteria"]
        if not _requires_present_and_usable_fact(criteria):
            continue

        fact = facts.get(subject_name)
        if fact is None or fact["status"] != "found":
            problems.append(subject_name)
    return problems


def _requires_present_and_usable_fact(criteria):
    if criteria.get("required"):
        return True

    comparison_keys = {
        "minimum",
        "maximum",
        "equals",
        "allowed_values",
        "disallowed_values",
    }
    return any(key in criteria for key in comparison_keys)


def _build_missing_fact_reason(subject_names):
    if len(subject_names) == 1:
        return (
            "Unable to evaluate because the required fact "
            f"'{subject_names[0]}' could not be established."
        )

    joined = ", ".join(subject_names)
    return (
        "Unable to evaluate because the required facts "
        f"{joined} could not be established."
    )


def _evaluate_policy(facts, evaluation_index):
    coverage_fact = facts["coverage"]
    coverage_rules = evaluation_index["coverage"]["criteria"]
    minimum = coverage_rules["minimum"]

    conclusion = "true" if coverage_fact["value"] >= minimum else "false"
    if conclusion == "true":
        reason = (
            f"Coverage is {coverage_fact['value']}%, which meets the required "
            f"{minimum}% threshold."
        )
    else:
        reason = (
            f"Coverage is {coverage_fact['value']}%, which is below the required "
            f"{minimum}% threshold."
        )

    return {
        "conclusion": conclusion,
        "facts": [coverage_fact],
        "reason": reason,
    }
