def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    status_evaluation = evaluation_index.get("status")
    if status_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a status evaluation with an equals criterion."
        )

    expected_status = _read_expected_status(status_evaluation)
    if expected_status is None:
        return _build_inconclusive_result(
            "This test requires status criteria.equals to be a text value."
        )

    status_fact = _extract_status_fact(evidence)
    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "The text evidence did not establish one unambiguous status value.",
        }

    return _evaluate_status(status_fact, expected_status)


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "text":
        return _build_inconclusive_result("This test expects text evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result(
            "This test only supports evaluator schema version 2."
        )
    if not isinstance(evidence, list):
        return _build_inconclusive_result(
            "This test expects text evidence as a list of lines."
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


def _read_expected_status(status_evaluation):
    criteria = status_evaluation.get("criteria", {})
    expected_status = criteria.get("equals")
    if isinstance(expected_status, str) and expected_status:
        return expected_status
    return None


def _split_label_value(line):
    raw_line = line.strip()
    if ":" not in raw_line:
        return None, None
    label, value = raw_line.split(":", 1)
    return label.strip().lower(), value.strip()


def _extract_status_fact(evidence):
    found_values = []
    for line in evidence:
        label, value = _split_label_value(line)
        if label == "status":
            found_values.append(value)

    unique_values = [value for value in found_values if value]
    if not unique_values:
        return {
            "name": "status",
            "value": None,
            "value_type": "text",
            "status": "not_found",
        }

    if len(set(unique_values)) > 1:
        return {
            "name": "status",
            "value": unique_values,
            "value_type": "text",
            "status": "invalid",
        }

    return {
        "name": "status",
        "value": unique_values[0],
        "value_type": "text",
        "status": "found",
    }


def _evaluate_status(status_fact, expected_status):
    actual_status = status_fact["value"]
    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"The text status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": (
            f"The text status is '{actual_status}', not '{expected_status}'."
        ),
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
