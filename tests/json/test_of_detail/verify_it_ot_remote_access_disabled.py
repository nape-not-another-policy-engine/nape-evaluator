def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    remote_access_evaluation = evaluation_index.get("remote_access_enabled")
    if remote_access_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a remote_access_enabled evaluation with an equals criterion."
        )

    expected_value = _read_boolean_equals(remote_access_evaluation)
    if expected_value is None:
        return _build_inconclusive_result(
            "This test requires remote_access_enabled criteria.equals to be boolean."
        )

    remote_access_fact = _extract_remote_access_fact(evidence)
    if remote_access_fact["status"] != "found":
        return _build_inconclusive_result(
            [remote_access_fact],
            "Unable to evaluate because the remote_access_enabled fact could not be established.",
        )

    return _evaluate_equals(remote_access_fact, expected_value)


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


def _extract_remote_access_fact(evidence):
    value = evidence.get("it_ot_boundary", {}).get("remote_access_enabled")
    if value is None:
        return {
            "name": "remote_access_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "remote_access_enabled",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "remote_access_enabled",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _evaluate_equals(remote_access_fact, expected_value):
    actual = remote_access_fact["value"]
    if actual == expected_value:
        return {
            "conclusion": "true",
            "facts": [remote_access_fact],
            "reason": (
                f"remote_access_enabled is {actual}, which matches the expected value."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [remote_access_fact],
        "reason": (
            f"remote_access_enabled is {actual}, which does not match the expected value {expected_value}."
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
