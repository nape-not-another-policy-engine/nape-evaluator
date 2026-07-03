def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    custody_evaluation = evaluation_index.get("chain_of_custody_complete")
    if custody_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a chain_of_custody_complete evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(custody_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires chain_of_custody_complete criteria.equals to be boolean."
        )

    custody_fact = _extract_custody_fact(evidence)
    if custody_fact["status"] != "found":
        return _build_inconclusive_result(
            [custody_fact],
            "Unable to evaluate because the chain_of_custody_complete fact could not be established.",
        )

    return _evaluate_equals(custody_fact, expected_value)


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


def _extract_custody_fact(evidence):
    value = evidence.get("cold_chain_exception", {}).get("chain_of_custody_complete")
    if value is None:
        return {
            "name": "chain_of_custody_complete",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "chain_of_custody_complete",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "chain_of_custody_complete",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(custody_fact, expected_value):
    actual = custody_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [custody_fact],
            "reason": (
                f"chain_of_custody_complete is {actual}, which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [custody_fact],
        "reason": (
            f"chain_of_custody_complete is {actual}, which does not match the expected value {expected_value}."
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
