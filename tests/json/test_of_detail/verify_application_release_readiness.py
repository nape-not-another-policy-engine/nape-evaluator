def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    expected_mfa = _read_boolean_equals(evaluation_index.get("mfa_required"))
    maximum_vulnerabilities = _read_integer_criterion(
        evaluation_index.get("critical_vulnerability_count"), "maximum"
    )
    expected_approval = _read_boolean_equals(
        evaluation_index.get("deployment_approval_present")
    )

    if (
        expected_mfa is None
        or maximum_vulnerabilities is None
        or expected_approval is None
    ):
        return _build_inconclusive_result(
            "This test requires mfa_required equals, critical_vulnerability_count maximum, and deployment_approval_present equals."
        )

    mfa_fact = _extract_mfa_fact(evidence)
    vulnerability_fact = _extract_count_fact(evidence)
    approval_fact = _extract_approval_fact(evidence)
    facts = [mfa_fact, vulnerability_fact, approval_fact]

    failed_establishment = []
    for fact in (mfa_fact, vulnerability_fact, approval_fact):
        if fact["status"] != "found":
            failed_establishment.append(fact["name"])
    if failed_establishment:
        joined = ", ".join(failed_establishment)
        return {
            "conclusion": "inconclusive",
            "facts": facts,
            "reason": (
                "Unable to evaluate application release readiness because these facts could not be "
                f"established cleanly: {joined}."
            ),
        }

    reasons = []
    conclusion = "true"

    if mfa_fact["value"] != expected_mfa:
        conclusion = "false"
        reasons.append(f"mfa_required is {mfa_fact['value']}, not {expected_mfa}.")

    if vulnerability_fact["value"] > maximum_vulnerabilities:
        conclusion = "false"
        reasons.append(
            "critical_vulnerability_count is "
            f"{vulnerability_fact['value']}, which exceeds the allowed maximum of {maximum_vulnerabilities}."
        )

    if approval_fact["value"] != expected_approval:
        conclusion = "false"
        reasons.append(
            f"deployment_approval_present is {approval_fact['value']}, not {expected_approval}."
        )

    if conclusion == "true":
        return {
            "conclusion": "true",
            "facts": facts,
            "reason": (
                "Application release readiness is satisfied: MFA is required, unresolved critical "
                "vulnerabilities are within threshold, and deployment approval is present."
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


def _read_integer_criterion(evaluation, key):
    if not isinstance(evaluation, dict):
        return None
    value = evaluation.get("criteria", {}).get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _extract_mfa_fact(evidence):
    value = evidence.get("application_release", {}).get("mfa_required")
    if value is None:
        return {
            "name": "mfa_required",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "mfa_required",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "mfa_required",
        "value": value,
        "value_type": "boolean",
        "status": "found",
    }


def _extract_count_fact(evidence):
    value = evidence.get("application_release", {}).get("critical_vulnerability_count")
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


def _extract_approval_fact(evidence):
    value = evidence.get("application_release", {}).get("deployment_approval_present")
    if value is None:
        return {
            "name": "deployment_approval_present",
            "value": None,
            "value_type": "boolean",
            "status": "not_found",
        }
    if not isinstance(value, bool):
        return {
            "name": "deployment_approval_present",
            "value": None,
            "value_type": "boolean",
            "status": "invalid",
        }
    return {
        "name": "deployment_approval_present",
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
