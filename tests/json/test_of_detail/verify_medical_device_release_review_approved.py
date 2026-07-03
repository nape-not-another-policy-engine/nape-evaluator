def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    status_evaluation = evaluation_index.get("release_review_status")
    if status_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a release_review_status evaluation with an equals criterion."
        )

    expected_status = _read_expected_status(status_evaluation)
    if expected_status is None:
        return _build_inconclusive_result(
            "This test requires release_review_status criteria.equals to be a text value."
        )

    status_fact = _extract_status_fact(evidence)
    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "The medical device release evidence did not provide a usable release review status.",
        }

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


def _read_expected_status(status_evaluation):
    expected_status = status_evaluation.get("criteria", {}).get("equals")
    if isinstance(expected_status, str) and expected_status:
        return expected_status
    return None


def _extract_status_fact(evidence):
    status = evidence.get("device_release", {}).get("release_review_status")
    return {
        "name": "release_review_status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }


def _evaluate_status(status_fact, expected_status):
    actual_status = status_fact["value"]
    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Release review status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": (
            f"Release review status is '{actual_status}', not '{expected_status}'."
        ),
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
