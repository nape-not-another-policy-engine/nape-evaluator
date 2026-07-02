"""Helpers for building the evaluator's stdout JSON contract."""

from typing import Any, Dict, Iterable, Optional, Sequence


def build_message(
    level: str,
    code: str,
    message: str,
    evidence_file: Optional[str] = None,
    test_file: Optional[str] = None,
    *,
    scope: str = "test",
    affected_tests: Optional[Sequence[str]] = None,
    stack_trace: Optional[str] = None,
) -> Dict[str, Any]:
    """Build one evaluator-owned message event in the public output shape."""

    return {
        "scope": scope,
        "level": level,
        "source": "evaluator",
        "code": code,
        "message": message,
        "evidence_file": evidence_file,
        "test_file": test_file,
        "affected_tests": list(affected_tests) if affected_tests is not None else None,
        "stack_trace": stack_trace,
    }


def build_summary(
    count: int,
    results: Iterable[Dict[str, Any]],
    messages: Iterable[Dict[str, Any]],
) -> Dict[str, int]:
    """Build aggregate result and evaluator-message counts for one invocation."""

    message_list = list(messages)
    summary = {
        "count": count,
        "ran": 0,
        "true": 0,
        "false": 0,
        "inconclusive": 0,
        "message_count": len(message_list),
        "message_info": 0,
        "message_warning": 0,
        "message_error": 0,
    }

    for result in results:
        execution = result.get("execution", {})
        if execution.get("executed", False):
            summary["ran"] += 1

        result_payload = result.get("result") or {}
        conclusion = result_payload.get("conclusion")
        if conclusion in ("true", "false", "inconclusive"):
            summary[conclusion] += 1

    for message in message_list:
        level = message.get("level")
        if level == "info":
            summary["message_info"] += 1
        elif level == "warning":
            summary["message_warning"] += 1
        elif level == "error":
            summary["message_error"] += 1

    return summary


def build_cli_output(
    count: int,
    results: Sequence[Dict[str, Any]],
    messages: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build the final machine-readable stdout JSON object."""

    result_list = list(results)
    message_list = list(messages)
    return {
        "results": result_list,
        "evaluator": {
            "messages": message_list,
            "summary": build_summary(count, result_list, message_list),
        },
    }
