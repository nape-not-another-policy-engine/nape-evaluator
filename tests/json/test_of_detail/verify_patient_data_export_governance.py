def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_ticket = _read_boolean_equals(
        evaluation_index.get("data_export_ticket_present")
    )
    expected_approval = _read_boolean_equals(
        evaluation_index.get("data_export_approval_present")
    )
    expected_retention = _read_expected_status(
        evaluation_index.get("retention_execution_status")
    )

    if (
        expected_ticket is None
        or expected_approval is None
        or expected_retention is None
    ):
        return _build_inconclusive_result(
            "This test requires data_export_ticket_present equals, data_export_approval_present equals, and retention_execution_status equals."
        )

    ticket_fact = _extract_boolean_fact(
        evidence, "data_export_ticket_present", "data_export_ticket_present"
    )
    approval_fact = _extract_boolean_fact(
        evidence, "data_export_approval_present", "data_export_approval_present"
    )
    retention_fact = _extract_text_fact(
        evidence, "retention_execution_status", "retention_execution_status"
    )
    facts = [ticket_fact, approval_fact, retention_fact]

    failed_establishment = []
    for fact in (ticket_fact, approval_fact, retention_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate patient-data export governance because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if ticket_fact["value"] != expected_ticket:
        conclusion = "false"
        reasons.append(
            f"data_export_ticket_present is {ticket_fact['value']}, not {expected_ticket}."
        )

    if approval_fact["value"] != expected_approval:
        conclusion = "false"
        reasons.append(
            f"data_export_approval_present is {approval_fact['value']}, not {expected_approval}."
        )

    if retention_fact["value"] != expected_retention:
        conclusion = "false"
        reasons.append(
            f"retention_execution_status is '{retention_fact['value']}', not '{expected_retention}'."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Patient-data export governance is satisfied: the export ticket is present, "
                "approval is present, and retention execution is completed."
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


def _extract_boolean_fact(evidence, key, name):
    value = evidence.get("patient_data_export", {}).get(key)
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


def _extract_text_fact(evidence, key, name):
    value = evidence.get("patient_data_export", {}).get(key)
    return {
        "name": name,
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
