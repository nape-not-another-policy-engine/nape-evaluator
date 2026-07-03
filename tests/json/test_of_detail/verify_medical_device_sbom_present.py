def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    sbom_evaluation = evaluation_index.get("sbom_present")
    if sbom_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a sbom_present evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(sbom_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires sbom_present criteria.equals to be boolean."
        )

    sbom_fact = _extract_sbom_fact(evidence)
    if sbom_fact["status"] != "found":
        return _build_inconclusive_result(
            [sbom_fact],
            "Unable to evaluate because the sbom_present fact could not be established.",
        )

    return _evaluate_equals(sbom_fact, expected_value)


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


def _read_boolean_equals(evaluation):
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_sbom_fact(evidence):
    value = evidence.get("device_release", {}).get("sbom_present")
    if value is None:
        return {
            "name": "sbom_present",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "sbom_present",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "sbom_present",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(sbom_fact, expected_value):
    actual = sbom_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [sbom_fact],
            "reason": f"sbom_present is {actual}, which matches the expected value.",
        }
    return {
        "conclusion": "false",
        "facts": [sbom_fact],
        "reason": f"sbom_present is {actual}, which does not match the expected value {expected_value}.",
    }


def _build_inconclusive_result(arg1, arg2=None):
    facts = [] if arg2 is None else arg1
    reason = arg1 if arg2 is None else arg2
    return {
        "conclusion": "inconclusive",
        "facts": facts,
        "reason": reason,
    }
