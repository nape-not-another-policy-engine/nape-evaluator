def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_status = _read_expected_status(
        evaluation_index.get("batch_release_status")
    )
    reviewer_expected = _read_boolean_equals(
        evaluation_index.get("quality_reviewer_present")
    )
    deviation_expected = _read_boolean_equals(
        evaluation_index.get("deviation_closed")
    )

    if (
        expected_status is None
        or reviewer_expected is None
        or deviation_expected is None
    ):
        return _build_inconclusive_result(
            "This test requires batch_release_status equals, quality_reviewer_present equals, and deviation_closed equals."
        )

    status_fact = _extract_text_fact(
        evidence, "batch_release_status", "batch_release_status"
    )
    reviewer_fact = _extract_boolean_fact(
        evidence, "quality_reviewer_present", "quality_reviewer_present"
    )
    deviation_fact = _extract_boolean_fact(
        evidence, "deviation_closed", "deviation_closed"
    )
    facts = [status_fact, reviewer_fact, deviation_fact]

    failed_establishment = []
    for fact in (status_fact, reviewer_fact, deviation_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate regulated quality batch release readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if status_fact["value"] != expected_status:
        conclusion = "false"
        reasons.append(
            f"batch_release_status is '{status_fact['value']}', not '{expected_status}'."
        )

    if reviewer_fact["value"] != reviewer_expected:
        conclusion = "false"
        reasons.append(
            f"quality_reviewer_present is {reviewer_fact['value']}, not {reviewer_expected}."
        )

    if deviation_fact["value"] != deviation_expected:
        conclusion = "false"
        reasons.append(
            f"deviation_closed is {deviation_fact['value']}, not {deviation_expected}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Regulated quality batch release readiness is satisfied: the batch release status is released, "
                "a quality reviewer is present, and the deviation is closed."
            ),
        }

    return {
        "conclusion": "false",
        "facts": facts,
        "reason": " ".join(reasons),
    }


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
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _read_boolean_equals(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_text_fact(evidence, key, name):
    value = evidence.get("quality_batch_release", {}).get(key)
    return {
        "name": name,
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_boolean_fact(evidence, key, name):
    value = evidence.get("quality_batch_release", {}).get(key)
    if value is None:
        return {
            "name": name,
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": name,
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": name,
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
