def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    reason_evaluation = evaluation_index.get("revocation_reason")
    if reason_evaluation is None:
        return _build_error_result(
            "This test requires a revocation_reason evaluation with an equals criterion."
        )

    expected_value = reason_evaluation.get("criteria", {}).get("equals", "__missing__")
    if expected_value is not None:
        return _build_error_result(
            "This test requires revocation_reason criteria.equals to be null."
        )

    reason_fact = _extract_revocation_reason_fact(evidence)
    if reason_fact["status"] != "found":
        return _build_inconclusive_result(
            [reason_fact],
            "Unable to evaluate because the revocation_reason fact could not be established.",
        )

    return {
        "conclusion": "true",
        "facts": [reason_fact],
        "reason": "revocation_reason is explicitly null as expected.",
    }


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


def _extract_revocation_reason_fact(evidence):
    container = evidence.get("access_grant", {})
    if "revocation_reason" not in container:
        return {
            "name": "revocation_reason",
            "value": None,
            "value_type": "null",
            "status": "not_found",
        }
    if container["revocation_reason"] is not None:
        return {
            "name": "revocation_reason",
            "value": container["revocation_reason"],
            "value_type": "null",
            "status": "invalid",
        }
    return {
        "name": "revocation_reason",
        "value": None,
        "value_type": "null",
        "status": "found",
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
