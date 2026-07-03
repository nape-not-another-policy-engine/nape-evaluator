def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    amount_evaluation = evaluation_index.get("settlement_difference_amount")
    if amount_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a settlement_difference_amount evaluation with a maximum criterion."
        )

    maximum = _read_numeric_criterion(amount_evaluation, "maximum")
    if maximum is None:
        return _build_inconclusive_result(
            "This test requires settlement_difference_amount criteria.maximum to be numeric."
        )

    amount_fact = _extract_amount_fact(evidence)
    if amount_fact["status"] != "found":
        return _build_inconclusive_result(
            [amount_fact],
            "Unable to evaluate because the settlement_difference_amount fact could not be established.",
        )

    return _evaluate_maximum(amount_fact, maximum)


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


def _read_numeric_criterion(evaluation, key):
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


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


def _evaluate_maximum(amount_fact, maximum):
    actual = amount_fact["value"]
    if actual <= maximum:
        return {
            "conclusion": "true",
            "facts": [amount_fact],
            "reason": (
                f"Settlement difference amount is {actual}, which is within the allowed maximum of {maximum}."
            ),
        }
    return {
        "conclusion": "false",
        "facts": [amount_fact],
        "reason": (
            f"Settlement difference amount is {actual}, which exceeds the allowed maximum of {maximum}."
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
