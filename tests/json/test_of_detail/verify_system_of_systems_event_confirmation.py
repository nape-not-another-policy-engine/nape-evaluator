def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_approval = _read_boolean_equals(
        evaluation_index.get("interconnection_approval_present")
    )
    expected_confirmation = _read_expected_status(
        evaluation_index.get("event_confirmation_status")
    )
    expected_match = _read_boolean_equals(
        evaluation_index.get("cross_system_state_match")
    )

    if (
        expected_approval is None
        or expected_confirmation is None
        or expected_match is None
    ):
        return _build_inconclusive_result(
            "This test requires interconnection_approval_present equals, event_confirmation_status equals, and cross_system_state_match equals."
        )

    approval_fact = _extract_approval_fact(evidence)
    confirmation_fact = _extract_confirmation_fact(evidence)
    match_fact = _extract_match_fact(evidence)
    facts = [approval_fact, confirmation_fact, match_fact]

    failed_establishment = []
    for fact in (approval_fact, confirmation_fact, match_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate system-of-systems event confirmation because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if approval_fact["value"] != expected_approval:
        conclusion = "false"
        reasons.append(
            f"interconnection_approval_present is {approval_fact['value']}, not {expected_approval}."
        )

    if confirmation_fact["value"] != expected_confirmation:
        conclusion = "false"
        reasons.append(
            f"event_confirmation_status is '{confirmation_fact['value']}', not '{expected_confirmation}'."
        )

    if match_fact["value"] != expected_match:
        conclusion = "false"
        reasons.append(
            f"cross_system_state_match is {match_fact['value']}, not {expected_match}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "System-of-systems event confirmation is satisfied: interconnection approval is present, "
                "the event is confirmed across systems, and the reported states match."
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


def _read_boolean_equals(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _read_expected_status(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, str) and value:
        return value
    return None


def _extract_approval_fact(evidence):
    value = evidence.get("system_confirmation", {}).get("interconnection", {}).get(
        "approval_id"
    )
    return {
        "name": "interconnection_approval_present",
        "value": value not in (None, ""),
        "value_type": "boolean",
        "status": "found",
    }


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


def _extract_match_fact(evidence):
    packet = evidence.get("system_confirmation", {})
    origin_state = packet.get("origin_system", {}).get("reported_state")
    receiving_state = packet.get("receiving_system", {}).get("reported_state")
    if not isinstance(origin_state, str) or not origin_state:
        return {
            "name": "cross_system_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(receiving_state, str) or not receiving_state:
        return {
            "name": "cross_system_state_match",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    return {
        "name": "cross_system_state_match",
        "value": origin_state == receiving_state,
        "value_type": "boolean",
        "status": "found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
