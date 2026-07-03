def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_approval = _read_expected_status(
        evaluation_index.get("transaction_approval_status")
    )
    expected_reconciliation = _read_expected_status(
        evaluation_index.get("reconciliation_status")
    )
    maximum_difference = _read_numeric_criterion(
        evaluation_index.get("settlement_difference_amount"), "maximum"
    )

    if (
        expected_approval is None
        or expected_reconciliation is None
        or maximum_difference is None
    ):
        return _build_inconclusive_result(
            "This test requires transaction_approval_status equals, reconciliation_status equals, and settlement_difference_amount maximum."
        )

    approval_fact = _extract_text_fact(
        evidence, "transaction_approval_status", "transaction_approval_status"
    )
    reconciliation_fact = _extract_text_fact(
        evidence, "reconciliation_status", "reconciliation_status"
    )
    difference_fact = _extract_amount_fact(evidence)
    facts = [approval_fact, reconciliation_fact, difference_fact]

    failed_establishment = []
    for fact in (approval_fact, reconciliation_fact, difference_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate payment settlement readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if approval_fact["value"] != expected_approval:
        conclusion = "false"
        reasons.append(
            f"transaction_approval_status is '{approval_fact['value']}', not '{expected_approval}'."
        )

    if reconciliation_fact["value"] != expected_reconciliation:
        conclusion = "false"
        reasons.append(
            f"reconciliation_status is '{reconciliation_fact['value']}', not '{expected_reconciliation}'."
        )

    if difference_fact["value"] > maximum_difference:
        conclusion = "false"
        reasons.append(
            "settlement_difference_amount is "
            f"{difference_fact['value']}, which exceeds the allowed maximum of {maximum_difference}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Payment settlement readiness is satisfied: the transaction is approved, the "
                "reconciliation is completed, and the settlement difference amount is within tolerance."
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


def _read_numeric_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _extract_text_fact(evidence, key, name):
    value = evidence.get("payment_settlement", {}).get(key)
    return {
        "name": name,
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_amount_fact(evidence):
    value = evidence.get("payment_settlement", {}).get("settlement_difference_amount")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return {
            "name": "settlement_difference_amount",
            "value": value,
            "value_type": "number",
            "status": "invalid" if value not in (None, "") else "not_found",
        }
    return {
        "name": "settlement_difference_amount",
        "value": float(value),
        "value_type": "number",
        "status": "found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
