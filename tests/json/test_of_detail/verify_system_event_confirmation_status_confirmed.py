def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    status_evaluation = evaluation_index.get("event_confirmation_status")
    if status_evaluation is None:
        return _build_inconclusive_result(
            "This test requires an event_confirmation_status evaluation with an equals criterion."
        )

    expected_status = _read_expected_status(status_evaluation)
    if expected_status is None:
        return _build_inconclusive_result(
            "This test requires event_confirmation_status criteria.equals to be a text value."
        )

    status_fact = _extract_confirmation_fact(evidence)
    if status_fact["status"] != "found":
        return _build_inconclusive_result(
            [status_fact],
            "Unable to evaluate because the event_confirmation_status fact could not be established.",
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


def _extract_confirmation_fact(evidence):
    packet = evidence.get("system_confirmation", {})
    event_id = packet.get("event", {}).get("event_id")
    if not isinstance(event_id, str) or not event_id:
        return {
            "name": "event_confirmation_status",
            "value": None,
            "value_type": "text",
            "status": "not_found",
        }

    origin_ids = packet.get("origin_system", {}).get("confirmed_event_ids", [])
    receiving_ids = packet.get("receiving_system", {}).get("confirmed_event_ids", [])
    if not isinstance(origin_ids, list) or not isinstance(receiving_ids, list):
        return {
            "name": "event_confirmation_status",
            "value": None,
            "value_type": "text",
            "status": "invalid",
        }

    confirmed = event_id in origin_ids and event_id in receiving_ids
    return {
        "name": "event_confirmation_status",
        "value": "confirmed" if confirmed else "not_confirmed",
        "value_type": "text",
        "status": "found",
    }


def _evaluate_status(status_fact, expected_status):
    actual_status = status_fact["value"]
    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Event confirmation status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": (
            f"Event confirmation status is '{actual_status}', not '{expected_status}'."
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
