def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_release = _read_expected_status(
        evaluation_index.get("maintenance_release_status")
    )
    expected_work_order = _read_expected_bool(
        evaluation_index.get("work_order_complete")
    )
    expected_restart = _read_expected_status(
        evaluation_index.get("restart_authorization_status")
    )

    if expected_release is None or expected_work_order is not True or expected_restart is None:
        return _build_inconclusive_result(
            "This test requires maintenance_release_status equals, work_order_complete equals true, and restart_authorization_status equals."
        )

    release_fact = _extract_release_fact(evidence)
    work_order_fact = _extract_work_order_fact(evidence)
    restart_fact = _extract_restart_fact(evidence)
    facts = [release_fact, work_order_fact, restart_fact]

    failed_establishment = []
    for fact in (release_fact, work_order_fact, restart_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate manufacturing line restart readiness because these facts "
                f"could not be established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if release_fact["value"] != expected_release:
        conclusion = "false"
        reasons.append(
            f"maintenance_release_status is '{release_fact['value']}', not '{expected_release}'."
        )

    if work_order_fact["value"] is not True:
        conclusion = "false"
        reasons.append("work_order_complete is not true.")

    if restart_fact["value"] != expected_restart:
        conclusion = "false"
        reasons.append(
            f"restart_authorization_status is '{restart_fact['value']}', not '{expected_restart}'."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Manufacturing line restart readiness is satisfied: maintenance release is approved, "
                "the work order is complete, and restart authorization is approved."
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


def _read_expected_bool(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    return value if isinstance(value, bool) else None


def _extract_release_fact(evidence):
    value = evidence.get("line_restart", {}).get("maintenance_release_status")
    return {
        "name": "maintenance_release_status",
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_work_order_fact(evidence):
    value = evidence.get("line_restart", {}).get("work_order_complete")
    return {
        "name": "work_order_complete",
        "value": value,
        "value_type": "boolean",
        "status": "found" if isinstance(value, bool) else "not_found",
    }


def _extract_restart_fact(evidence):
    value = evidence.get("line_restart", {}).get("restart_authorization_status")
    return {
        "name": "restart_authorization_status",
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
