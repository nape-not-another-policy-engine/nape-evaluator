def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    status_evaluation = evaluation_index.get("boundary_control_status")
    if status_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a boundary_control_status evaluation with an equals criterion."
        )

    expected_status = _read_expected_status(status_evaluation)
    if expected_status is None:
        return _build_inconclusive_result(
            "This test requires boundary_control_status criteria.equals to be a text value."
        )

    status_fact = _extract_status_fact(evidence)
    if status_fact["status"] != "found":
        return _build_inconclusive_result(
            [status_fact],
            "Unable to evaluate because the boundary_control_status fact could not be established.",
        )

    return _evaluate_status(status_fact, expected_status)


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


def _read_expected_status(evaluation):
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _extract_status_fact(evidence):
    value = evidence.get("it_ot_boundary", {}).get("boundary_control_status")
    return {
        "name": "boundary_control_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _evaluate_status(status_fact, expected_status):
    actual_status = status_fact["value"]
    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Boundary control status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": (
            f"Boundary control status is '{actual_status}', not '{expected_status}'."
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
