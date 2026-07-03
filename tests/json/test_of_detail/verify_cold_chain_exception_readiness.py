def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    maximum_excursions = _read_integer_criterion(
        evaluation_index.get("temperature_excursion_count"), "maximum"
    )
    expected_custody = _read_boolean_equals(
        evaluation_index.get("chain_of_custody_complete")
    )
    expected_exception_closed = _read_boolean_equals(
        evaluation_index.get("exception_closed")
    )

    if (
        maximum_excursions is None
        or expected_custody is None
        or expected_exception_closed is None
    ):
        return _build_inconclusive_result(
            "This test requires temperature_excursion_count maximum, chain_of_custody_complete equals, and exception_closed equals."
        )

    excursion_fact = _extract_count_fact(evidence)
    custody_fact = _extract_boolean_fact(
        evidence, "chain_of_custody_complete", "chain_of_custody_complete"
    )
    exception_fact = _extract_boolean_fact(
        evidence, "exception_closed", "exception_closed"
    )
    facts = [excursion_fact, custody_fact, exception_fact]

    failed_establishment = []
    for fact in (excursion_fact, custody_fact, exception_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate cold-chain exception readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if excursion_fact["value"] > maximum_excursions:
        conclusion = "false"
        reasons.append(
            "temperature_excursion_count is "
            f"{excursion_fact['value']}, which exceeds the allowed maximum of {maximum_excursions}."
        )

    if custody_fact["value"] != expected_custody:
        conclusion = "false"
        reasons.append(
            f"chain_of_custody_complete is {custody_fact['value']}, not {expected_custody}."
        )

    if exception_fact["value"] != expected_exception_closed:
        conclusion = "false"
        reasons.append(
            f"exception_closed is {exception_fact['value']}, not {expected_exception_closed}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Cold-chain exception readiness is satisfied: the temperature excursion count is within "
                "threshold, chain of custody is complete, and the exception is closed."
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


def _read_integer_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _read_boolean_equals(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _extract_count_fact(evidence):
    value = evidence.get("cold_chain_exception", {}).get("temperature_excursion_count")
    if value is None:
        return {
            "name": "temperature_excursion_count",
            "value": None,
            "value_type": "integer",
            "status": "not_found",
        }
    if not isinstance(value, int) or isinstance(value, bool):
        return {
            "name": "temperature_excursion_count",
            "value": None,
            "value_type": "integer",
            "status": "invalid",
        }
    return {
        "name": "temperature_excursion_count",
        "value": value,
        "value_type": "integer",
        "status": "found",
    }


def _extract_boolean_fact(evidence, key, name):
    value = evidence.get("cold_chain_exception", {}).get(key)
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


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
