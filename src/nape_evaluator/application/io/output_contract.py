from typing import Any, Dict, List


def build_message(
    level,
    code,
    message,
    evidence_file=None,
    test_file=None,
    test_parameters_source=None,
):
    return {
        "level": level,
        "source": "evaluator",
        "code": code,
        "message": message,
        "evidence_file": evidence_file,
        "test_file": test_file,
        "test_parameters_source": test_parameters_source,
    }


def build_summary(count, results, messages):
    summary = {
        "count": count,
        "ran": 0,
        "pass": 0,
        "fail": 0,
        "inconclusive": 0,
        "error": 0,
        "message_count": len(messages),
        "message_info": 0,
        "message_warning": 0,
        "message_error": 0,
    }
    for result in results:
        if not result.get("executed", True):
            continue
        summary["ran"] += 1
        outcome = result.get("outcome")
        if outcome in ("pass", "fail", "inconclusive", "error"):
            summary[outcome] += 1
    for message in messages:
        level = message.get("level")
        if level == "info":
            summary["message_info"] += 1
        elif level == "warning":
            summary["message_warning"] += 1
        elif level == "error":
            summary["message_error"] += 1
    return summary


def build_cli_output(
    count: int, results: List[Dict[str, Any]], messages: List[Dict[str, Any]]
):
    return {
        "results": results,
        "evaluator": {
            "messages": messages,
            "summary": build_summary(count, results, messages),
        },
    }
