def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_status = _read_expected_status(
        evaluation_index.get("release_review_status")
    )
    expected_sbom = _read_boolean_equals(evaluation_index.get("sbom_present"))
    maximum_critical = _read_integer_criterion(
        evaluation_index.get("critical_vulnerability_count"), "maximum"
    )

    if expected_status is None or expected_sbom is None or maximum_critical is None:
        return _build_inconclusive_result(
            "This test requires release_review_status equals, sbom_present equals, and critical_vulnerability_count maximum."
        )

    status_fact = _extract_text_fact(
        evidence, "release_review_status", "release_review_status"
    )
    sbom_fact = _extract_boolean_fact(evidence, "sbom_present", "sbom_present")
    vulnerability_fact = _extract_count_fact(evidence)
    facts = [status_fact, sbom_fact, vulnerability_fact]

    failed_establishment = []
    for fact in (status_fact, sbom_fact, vulnerability_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate medical device release packet readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if status_fact["value"] != expected_status:
        conclusion = "false"
        reasons.append(
            f"release_review_status is '{status_fact['value']}', not '{expected_status}'."
        )

    if sbom_fact["value"] != expected_sbom:
        conclusion = "false"
        reasons.append(
            f"sbom_present is {sbom_fact['value']}, not {expected_sbom}."
        )

    if vulnerability_fact["value"] > maximum_critical:
        conclusion = "false"
        reasons.append(
            "critical_vulnerability_count is "
            f"{vulnerability_fact['value']}, which exceeds the allowed maximum of {maximum_critical}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Medical device release packet readiness is satisfied: the release review is approved, "
                "the SBOM is present, and unresolved critical vulnerabilities are within threshold."
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


def _read_boolean_equals(evaluation):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get("equals")
    if isinstance(value, bool):
        return value
    return None


def _read_integer_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _extract_text_fact(evidence, key, name):
    value = evidence.get("device_release", {}).get(key)
    return {
        "name": name,
        "value": value,
        "value_type": "text",
        "status": "found" if value not in (None, "") else "not_found",
    }


def _extract_boolean_fact(evidence, key, name):
    value = evidence.get("device_release", {}).get(key)
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


def _extract_count_fact(evidence):
    value = evidence.get("device_release", {}).get("critical_vulnerability_count")
    if value is None:
        return {
            "name": "critical_vulnerability_count",
            "value": None,
            "value_type": "integer",
            "status": "not_found",
        }
    if not isinstance(value, int) or isinstance(value, bool):
        return {
            "name": "critical_vulnerability_count",
            "value": None,
            "value_type": "integer",
            "status": "invalid",
        }
    return {
        "name": "critical_vulnerability_count",
        "value": value,
        "value_type": "integer",
        "status": "found",
    }


def _build_inconclusive_result(reason):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": reason,
    }
