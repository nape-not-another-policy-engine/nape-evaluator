"""Strict provider boundary for one NAPE Evaluator V2 Action occurrence.

This module owns request admission and worker supervision.  It deliberately
does not import the historical evaluator implementation: the public legacy
lane and the discriminator-selected V2 lane are separate contracts.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import signal
import stat
import subprocess
import sys
import ast
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple


CONTRACT = "attestify.nape-evaluator.action-invocation/v2"
RUNNER_PROFILE = "attestify-python-test-development-v1"
MAX_REQUEST_BYTES = 1_048_576
MAX_ENCLOSING_RESPONSE_BYTES = 1_114_112
MAX_EVIDENCE_BYTES = 268_435_456
MAX_TEST_BYTES = 33_554_432
MAX_WORK_UNITS = 100_000_000
MAX_RESULT_BYTES = 1_048_576
WALL_WATCHDOG_SECONDS = 60

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_MEDIA_TYPE_RE = re.compile(
    r"^[a-z0-9][a-z0-9!#$&^_.+-]*/[a-z0-9][a-z0-9!#$&^_.+-]*$"
)
_FACT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

_DIAGNOSTICS = {
    "completed_invalid_result_contract": (
        "completed-invalid-result-contract-v1",
        "The Test of Detail returned an invalid result structure.",
    ),
    "completed_result_limit_exceeded": (
        "completed-result-limit-exceeded-v1",
        "The Test of Detail result exceeded its approved limit.",
    ),
    "evaluator_request_invalid": (
        "evaluator-request-invalid-v1",
        "The evaluator request is invalid.",
    ),
    "evidence_argument_integrity_failed": (
        "evidence-argument-integrity-failed-v1",
        "The evaluator evidence argument did not match the admitted evidence.",
    ),
    "invalid_metadata_contract": (
        "invalid-metadata-contract-v1",
        "The evaluator metadata did not match the admitted invocation.",
    ),
    "runner_activation_failed": (
        "runner-activation-failed-v1",
        "The approved Runner could not activate a fresh execution realm.",
    ),
    "runner_profile_unsupported": (
        "runner-profile-unsupported-v1",
        "The requested Runner Profile is unsupported.",
    ),
    "test_call_depth_exceeded": (
        "test-call-depth-exceeded-v1",
        "The Test of Detail exhausted its deterministic call-depth limit.",
    ),
    "test_cpu_backstop_exceeded": (
        "test-cpu-backstop-exceeded-v1",
        "The Test of Detail exceeded its CPU-time backstop.",
    ),
    "test_digest_mismatch": (
        "test-digest-mismatch-v1",
        "The Test of Detail bytes did not match the admitted digest.",
    ),
    "test_exception": (
        "test-exception-v1",
        "The Test of Detail terminated with an unhandled exception.",
    ),
    "test_execution_work_limit_exceeded": (
        "test-execution-work-limit-exceeded-v1",
        "The Test of Detail exhausted its deterministic execution-work limit.",
    ),
    "test_memory_backstop_exceeded": (
        "test-memory-backstop-exceeded-v1",
        "The Test of Detail exceeded its physical-memory backstop.",
    ),
    "test_sandbox_capability_violation": (
        "test-sandbox-capability-violation-v1",
        "The Test of Detail attempted a denied sandbox capability.",
    ),
    "test_wall_watchdog_expired": (
        "test-wall-watchdog-expired-v1",
        "The Test of Detail exceeded its wall-clock watchdog.",
    ),
    "test_worker_lost": (
        "test-worker-lost-v1",
        "The isolated Test worker was lost after activation.",
    ),
}


class RequestRejected(Exception):
    def __init__(self, code: str = "evaluator_request_invalid"):
        super().__init__(code)
        self.code = code


class IntegrityFailed(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class _DuplicateMember(Exception):
    pass


def is_versioned_request(candidate: Any) -> bool:
    """Route discriminator-first, including unknown/mixed contract inputs."""
    return isinstance(candidate, dict) and "contract" in candidate


def _strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateMember
        result[key] = value
    return result


def _reject_nonfinite(_token):
    raise ValueError("non-finite number")


def process_versioned_json(raw: bytes) -> Dict[str, Any]:
    """Decode the exact V2 frame with duplicate and non-finite rejection."""
    try:
        if len(raw) > MAX_REQUEST_BYTES or raw.startswith(b"\xef\xbb\xbf"):
            raise ValueError
        candidate = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        _DuplicateMember,
        ValueError,
    ):
        return _boundary(
            "request-rejected",
            "evaluator_request_invalid",
            "runner-call-validation",
        )
    return process_versioned_request(candidate, raw_byte_count=len(raw))


def _diagnostic(code: str, phase: str) -> Dict[str, str]:
    reason_template, _ = _DIAGNOSTICS[code]
    return {"code": code, "phase": phase, "reason_template": reason_template}


def _boundary(disposition: str, code: str, phase: str) -> Dict[str, Any]:
    return {
        "contract": CONTRACT,
        "disposition": disposition,
        "diagnostic": _diagnostic(code, phase),
    }


def _engine_result(reason: str) -> Dict[str, Any]:
    return {"conclusion": "inconclusive", "facts": [], "reason": reason}


def _execution(status: str, phase: str, call_count: int) -> Dict[str, Any]:
    return {
        "executed": status != "blocked",
        "status": status,
        "phase": phase,
        "evaluate_call_count": call_count,
        "automatic_retry_count": 0,
    }


def _contained(
    code: str,
    execution_phase: str,
    *,
    diagnostic_phase: Optional[str] = None,
    status: str = "terminated",
    call_count: int = 1,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    _, default_message = _DIAGNOSTICS[code]
    if code == "completed_invalid_result_contract":
        validation = {"contract": "failed", "limit": "not-evaluated"}
        execution = _execution("completed", "result-validation", 1)
        contained_reason = (
            reason or "The Action produced the contained invalid outcome."
        )
    elif code == "completed_result_limit_exceeded":
        validation = {"contract": "passed", "limit": "failed"}
        execution = _execution("completed", "result-validation", 1)
        contained_reason = (
            reason or "The Action produced the contained over-limit outcome."
        )
    else:
        validation = {"contract": "not-applicable", "limit": "not-applicable"}
        execution = _execution(status, execution_phase, call_count)
        contained_reason = reason or default_message
    return {
        "contract": CONTRACT,
        "disposition": "occurrence-result",
        "execution": execution,
        "result_validation": validation,
        "semantic_owner": "verification-engine",
        "result": _engine_result(contained_reason),
        "diagnostic": _diagnostic(
            code, diagnostic_phase if diagnostic_phase is not None else execution_phase
        ),
    }


def _valid(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract": CONTRACT,
        "disposition": "occurrence-result",
        "execution": _execution("completed", "evaluate-call", 1),
        "result_validation": {"contract": "passed", "limit": "passed"},
        "semantic_owner": "test-of-detail",
        "result": result,
        "diagnostic": None,
    }


def _expect_exact_object(
    candidate: Any, required: Iterable[str], *, code: str = "evaluator_request_invalid"
) -> Mapping[str, Any]:
    required_set = set(required)
    if (
        not isinstance(candidate, dict)
        or set(candidate.keys()) != required_set
        or any(not isinstance(key, str) for key in candidate)
    ):
        raise RequestRejected(code)
    return candidate


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_relative_path(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
        or "\\" in value
        or "\x00" in value
    ):
        raise RequestRejected()
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise RequestRejected()
    return value


def _validate_request(candidate: Any, raw_byte_count: Optional[int]) -> Mapping[str, Any]:
    if raw_byte_count is not None and raw_byte_count > MAX_REQUEST_BYTES:
        raise RequestRejected()
    request = _expect_exact_object(
        candidate,
        (
            "contract",
            "workspace_root",
            "evidence",
            "test",
            "evaluations",
            "metadata",
            "limits",
        ),
    )
    if request["contract"] != CONTRACT:
        raise RequestRejected()

    workspace = request["workspace_root"]
    if (
        not isinstance(workspace, str)
        or len(workspace) < 2
        or not workspace.startswith("/")
        or "\\" in workspace
        or "\x00" in workspace
        or os.path.normpath(workspace) != workspace
    ):
        raise RequestRejected()

    evidence = _expect_exact_object(
        request["evidence"],
        ("file", "argument_digest", "argument_byte_count", "media_type", "representation"),
    )
    _validate_relative_path(evidence["file"])
    if not isinstance(evidence["argument_digest"], str) or not _SHA256_RE.fullmatch(
        evidence["argument_digest"]
    ):
        raise RequestRejected()
    if not _is_int(evidence["argument_byte_count"]) or not (
        0 <= evidence["argument_byte_count"] <= MAX_EVIDENCE_BYTES
    ):
        raise RequestRejected()
    if (
        not isinstance(evidence["media_type"], str)
        or len(evidence["media_type"]) > 255
        or not _MEDIA_TYPE_RE.fullmatch(evidence["media_type"])
    ):
        raise RequestRejected()
    if evidence["representation"] != "opaque":
        raise RequestRejected()

    test = _expect_exact_object(
        request["test"], ("file", "content_digest", "byte_count", "runner_profile")
    )
    _validate_relative_path(test["file"])
    if not isinstance(test["content_digest"], str) or not _SHA256_RE.fullmatch(
        test["content_digest"]
    ):
        raise RequestRejected()
    if not _is_int(test["byte_count"]) or not (
        0 <= test["byte_count"] <= MAX_TEST_BYTES
    ):
        raise RequestRejected()
    if not isinstance(test["runner_profile"], str):
        raise RequestRejected()
    if test["runner_profile"] != RUNNER_PROFILE:
        raise RequestRejected("runner_profile_unsupported")

    if request["evaluations"] != []:
        raise RequestRejected()

    try:
        metadata = _expect_exact_object(
            request["metadata"],
            (
                "evidence_media_type",
                "evidence_representation",
                "evaluator_contract_version",
            ),
            code="invalid_metadata_contract",
        )
    except RequestRejected:
        raise RequestRejected("invalid_metadata_contract")
    if (
        metadata["evidence_media_type"] != evidence["media_type"]
        or metadata["evidence_representation"] != "opaque"
        or metadata["evaluator_contract_version"] != "2"
    ):
        raise RequestRejected("invalid_metadata_contract")

    limits = _expect_exact_object(
        request["limits"],
        ("maximum_execution_work_units", "maximum_result_bytes"),
    )
    if not _is_int(limits["maximum_execution_work_units"]) or not (
        1 <= limits["maximum_execution_work_units"] <= MAX_WORK_UNITS
    ):
        raise RequestRejected()
    if not _is_int(limits["maximum_result_bytes"]) or not (
        1 <= limits["maximum_result_bytes"] <= MAX_RESULT_BYTES
    ):
        raise RequestRejected()
    return request


def _validate_workspace(workspace: str) -> int:
    try:
        info = os.lstat(workspace)
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise OSError
        if hasattr(os, "geteuid") and info.st_uid != os.geteuid():
            raise OSError
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise OSError
        flags = os.O_RDONLY
        flags |= getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        return os.open(workspace, flags)
    except (OSError, ValueError):
        raise RequestRejected()


def _read_verified_file(
    root_fd: int,
    relative_path: str,
    expected_bytes: int,
    expected_digest: str,
    *,
    failure_code: str,
) -> bytes:
    current_fd = os.dup(root_fd)
    try:
        parts = relative_path.split("/")
        for part in parts[:-1]:
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            flags |= getattr(os, "O_NOFOLLOW", 0)
            next_fd = os.open(part, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        file_fd = os.open(parts[-1], flags, dir_fd=current_fd)
        try:
            info = os.fstat(file_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size != expected_bytes:
                raise IntegrityFailed(failure_code)
            chunks = []
            remaining = expected_bytes
            while remaining:
                chunk = os.read(file_fd, min(1_048_576, remaining))
                if not chunk:
                    raise IntegrityFailed(failure_code)
                chunks.append(chunk)
                remaining -= len(chunk)
            if os.read(file_fd, 1):
                raise IntegrityFailed(failure_code)
            payload = b"".join(chunks)
            digest = "sha256:" + hashlib.sha256(payload).hexdigest()
            if digest != expected_digest:
                raise IntegrityFailed(failure_code)
            return payload
        finally:
            os.close(file_fd)
    except IntegrityFailed:
        raise
    except (OSError, ValueError):
        raise IntegrityFailed(failure_code)
    finally:
        os.close(current_fd)


def _validate_json_value(value: Any, *, depth: int = 0) -> bool:
    if depth > 128:
        return False
    if value is None or isinstance(value, (str, bool, int)):
        return not isinstance(value, str) or not any(
            0xD800 <= ord(ch) <= 0xDFFF for ch in value
        )
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_validate_json_value(item, depth=depth + 1) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str)
            and _validate_json_value(key)
            and _validate_json_value(item, depth=depth + 1)
            for key, item in value.items()
        )
    return False


def _validate_semantic_result(candidate: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(candidate, dict) or set(candidate) != {
        "conclusion",
        "facts",
        "reason",
    }:
        return None
    if candidate["conclusion"] not in ("true", "false", "inconclusive"):
        return None
    reason = candidate["reason"]
    facts = candidate["facts"]
    if (
        not isinstance(reason, str)
        or not (1 <= len(reason) <= 65_536)
        or not isinstance(facts, list)
        or len(facts) > 256
    ):
        return None
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) != {
            "name",
            "value",
            "value_type",
            "status",
        }:
            return None
        if (
            not isinstance(fact["name"], str)
            or not (1 <= len(fact["name"]) <= 128)
            or not _FACT_NAME_RE.fullmatch(fact["name"])
        ):
            return None
        if fact["status"] == "found":
            if fact["value_type"] not in (
                "text",
                "integer",
                "number",
                "boolean",
                "date",
                "datetime",
                "duration",
                "array",
                "object",
            ):
                return None
        elif fact["status"] in ("not_found", "invalid"):
            if fact["value"] is not None or fact["value_type"] is not None:
                return None
        else:
            return None
    return candidate if _validate_json_value(candidate) else None


def _preflight_source(source: bytes) -> None:
    """Perform the frozen syntax and ABI admission before realm activation."""
    try:
        if source.startswith(b"\xef\xbb\xbf"):
            raise ValueError
        source_text = source.decode("utf-8", errors="strict")
        tree = ast.parse(source_text, filename="<admitted-test>", mode="exec")
        # The isolated worker repeats this exact profile admission before
        # execution. Importing the validator here does not activate Test code.
        from .worker import _Admission, _validate_abi

        _Admission().visit(tree)
        _validate_abi(tree)
    except (Exception, UnicodeDecodeError, SyntaxError, ValueError):
        raise RequestRejected()


def _format_float(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("non-finite JSON number")
    if value == 0:
        return "0"
    text = repr(value).lower()
    if "e" not in text:
        return text
    mantissa, exponent = text.split("e")
    exponent_value = int(exponent)
    sign_prefix = "-" if mantissa.startswith("-") else ""
    unsigned = mantissa.lstrip("-")
    fractional_digits = (
        len(unsigned) - unsigned.find(".") - 1 if "." in unsigned else 0
    )
    digits = unsigned.replace(".", "")
    decimal_position = len(digits) - fractional_digits + exponent_value
    decimal_exponent = decimal_position - 1
    if -6 <= decimal_exponent < 21:
        if decimal_position <= 0:
            return sign_prefix + "0." + ("0" * (-decimal_position)) + digits
        if decimal_position >= len(digits):
            return sign_prefix + digits + ("0" * (decimal_position - len(digits)))
        return (
            sign_prefix
            + digits[:decimal_position]
            + "."
            + digits[decimal_position:]
        )
    scientific_mantissa = digits[0]
    if len(digits) > 1:
        scientific_mantissa += "." + digits[1:].rstrip("0")
    sign = "+" if exponent_value >= 0 else "-"
    return f"{sign_prefix}{scientific_mantissa}e{sign}{abs(decimal_exponent)}"


def _jcs(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _format_float(value)
    if isinstance(value, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise ValueError("surrogate")
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_jcs(item) for item in value) + "]"
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("non-string key")
        ordered = sorted(value, key=lambda key: key.encode("utf-16-be"))
        return "{" + ",".join(_jcs(key) + ":" + _jcs(value[key]) for key in ordered) + "}"
    raise ValueError("non-JSON value")


def serialize_response(response: Mapping[str, Any]) -> bytes:
    encoded = _jcs(dict(response)).encode("utf-8") + b"\n"
    if len(encoded) > MAX_ENCLOSING_RESPONSE_BYTES:
        fallback = _contained(
            "completed_result_limit_exceeded",
            "result-validation",
        )
        encoded = _jcs(fallback).encode("utf-8") + b"\n"
    return encoded


def _run_worker(
    workspace: str,
    source: bytes,
    evidence: bytes,
    metadata: Mapping[str, Any],
    maximum_work: int,
) -> Dict[str, Any]:
    worker = Path(__file__).with_name("worker.py").resolve()
    control = {
        "source_hex": source.hex(),
        "evidence_hex": evidence.hex(),
        "metadata": dict(metadata),
        "maximum_execution_work_units": maximum_work,
    }
    control_bytes = json.dumps(control, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
    }
    try:
        process = subprocess.Popen(
            [os.path.abspath(sys.executable), "-I", "-B", str(worker)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
            env=environment,
            close_fds=True,
            start_new_session=True,
        )
    except (OSError, ValueError):
        return {"kind": "blocked", "code": "runner_activation_failed"}
    try:
        stdout, stderr = process.communicate(
            control_bytes, timeout=WALL_WATCHDOG_SECONDS
        )
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            process.kill()
        _stdout, stderr = process.communicate()
        execution_phase, call_count = _worker_progress(stderr)
        return {
            "kind": "contained",
            "code": "test_wall_watchdog_expired",
            "phase": execution_phase,
            "diagnostic_phase": "worker-supervision",
            "call_count": call_count,
        }
    if len(stdout) > MAX_ENCLOSING_RESPONSE_BYTES:
        execution_phase, call_count = _worker_progress(stderr)
        return {
            "kind": "contained",
            "code": "test_worker_lost",
            "phase": execution_phase,
            "diagnostic_phase": "worker-supervision",
            "call_count": call_count,
        }
    try:
        worker_result = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        if process.returncode is not None and process.returncode < 0:
            code = (
                "test_cpu_backstop_exceeded"
                if -process.returncode == getattr(signal, "SIGXCPU", -1)
                else "test_worker_lost"
            )
            execution_phase, call_count = _worker_progress(stderr)
            return {
                "kind": "contained",
                "code": code,
                "phase": execution_phase,
                "diagnostic_phase": "worker-supervision",
                "call_count": call_count,
            }
        execution_phase, call_count = _worker_progress(stderr)
        if call_count == 0 and execution_phase == "realm-activation":
            return {"kind": "blocked", "code": "runner_activation_failed"}
        return {
            "kind": "contained",
            "code": "test_worker_lost",
            "phase": execution_phase,
            "diagnostic_phase": "worker-supervision",
            "call_count": call_count,
        }
    if not isinstance(worker_result, dict):
        execution_phase, call_count = _worker_progress(stderr)
        return {
            "kind": "contained",
            "code": "test_worker_lost",
            "phase": execution_phase,
            "diagnostic_phase": "worker-supervision",
            "call_count": call_count,
        }
    return worker_result


def _worker_progress(stderr: bytes) -> Tuple[str, int]:
    if b"ATTESTIFY_EVALUATE_READY\n" in stderr:
        return "evaluate-call", 1
    if b"ATTESTIFY_WORKER_READY\n" in stderr:
        return "module-initialization", 0
    return "realm-activation", 0


def process_versioned_request(
    candidate: Any, *, raw_byte_count: Optional[int] = None
) -> Dict[str, Any]:
    """Admit and execute one closed V2 request without leaking protected detail."""
    try:
        request = _validate_request(candidate, raw_byte_count)
        root_fd = _validate_workspace(request["workspace_root"])
        try:
            evidence = _read_verified_file(
                root_fd,
                request["evidence"]["file"],
                request["evidence"]["argument_byte_count"],
                request["evidence"]["argument_digest"],
                failure_code="evidence_argument_integrity_failed",
            )
            source = _read_verified_file(
                root_fd,
                request["test"]["file"],
                request["test"]["byte_count"],
                request["test"]["content_digest"],
                failure_code="test_digest_mismatch",
            )
            _preflight_source(source)
        finally:
            os.close(root_fd)
    except RequestRejected as exc:
        phase = (
            "runner-profile-selection"
            if exc.code == "runner_profile_unsupported"
            else "runner-call-validation"
        )
        return _boundary("request-rejected", exc.code, phase)
    except IntegrityFailed as exc:
        return _boundary("integrity-failed", exc.code, "runner-call-validation")

    worker_result = _run_worker(
        request["workspace_root"],
        source,
        evidence,
        request["metadata"],
        request["limits"]["maximum_execution_work_units"],
    )
    kind = worker_result.get("kind")
    if kind == "blocked":
        return _contained(
            worker_result.get("code", "runner_activation_failed"),
            "realm-activation",
            status="blocked",
            call_count=0,
        )
    if kind == "contained":
        phase = worker_result.get("phase", "evaluate-call")
        return _contained(
            worker_result.get("code", "test_worker_lost"),
            phase,
            diagnostic_phase=worker_result.get("diagnostic_phase"),
            status="terminated",
            call_count=worker_result.get("call_count", 1),
        )
    if kind != "returned":
        return _contained("test_worker_lost", "evaluate-call")

    result = _validate_semantic_result(worker_result.get("result"))
    if result is None:
        return _contained(
            "completed_invalid_result_contract", "result-validation"
        )
    try:
        semantic_bytes = _jcs(result).encode("utf-8")
    except ValueError:
        return _contained(
            "completed_invalid_result_contract", "result-validation"
        )
    if len(semantic_bytes) > request["limits"]["maximum_result_bytes"]:
        return _contained(
            "completed_result_limit_exceeded", "result-validation"
        )
    return _valid(result)
