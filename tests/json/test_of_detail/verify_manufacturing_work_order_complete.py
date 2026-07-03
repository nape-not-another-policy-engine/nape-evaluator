def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    work_order_evaluation = evaluation_index.get("work_order_complete")
    if work_order_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a work_order_complete evaluation with an equals criterion."
        )

    expected_value = _read_expected_value(work_order_evaluation)
    if expected_value is not True:
        return _build_inconclusive_result(
            "This test requires work_order_complete criteria.equals to be true."
        )

    work_order_fact = _extract_work_order_fact(evidence)
    if work_order_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [work_order_fact],
            "reason": "The manufacturing evidence did not establish a usable work_order_complete value.",
        }

    if work_order_fact["value"] is True:
        return {
            "conclusion": "true",
            "facts": [work_order_fact],
            "reason": "The manufacturing work order is complete.",
        }

    return {
        "conclusion": "false",
        "facts": [work_order_fact],
        "reason": "The manufacturing work order is not complete.",
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


def _read_expected_value(work_order_evaluation):
    value = work_order_evaluation.get("criteria", {}).get("equals")
    return value if isinstance(value, bool) else None


def _extract_work_order_fact(evidence):
    value = evidence.get("line_restart", {}).get("work_order_complete")
    return {
        "name": "work_order_complete",
        "value": value,
        "value_type": "boolean",
        "status": "found" if isinstance(value, bool) else "not_found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
