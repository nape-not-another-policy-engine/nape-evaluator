import argparse
import json
import sys
import traceback

from nape_evaluator.application.driver.evidence_gateway import DEFAULT_EVIDENCE_GATEWAY
from nape_evaluator.application.driver.test_of_detail_gateway import (
    DEFAULT_TEST_OF_DETAIL_GATEWAY,
)
from nape_evaluator.application.io.output_contract import build_message
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    EvaluateEvidenceResponse,
    RequestValidationError,
)
from nape_evaluator.domain.use_cases import evaluate_request


class CliInvocationError(Exception):
    """Raised when evaluator invocation input cannot cross the CLI boundary."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        evidence_file=None,
        affected_tests=None,
        stack_trace=None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.evidence_file = evidence_file
        self.affected_tests = list(affected_tests or [])
        self.stack_trace = stack_trace

    def to_cli_output(self):
        return EvaluateEvidenceResponse(
            count=0,
            results=(),
            messages=(
                build_message(
                    "error",
                    self.code,
                    self.message,
                    self.evidence_file,
                    None,
                    scope="request",
                    affected_tests=self.affected_tests,
                    stack_trace=self.stack_trace,
                ),
            ),
        ).to_cli_output()


class NonExitingArgumentParser(argparse.ArgumentParser):
    """Argument parser that raises bounded CLI invocation errors instead of exiting."""

    def error(self, message):
        raise CliInvocationError("cli_argument_error", message)


def build_parser():
    parser = NonExitingArgumentParser(
        description="Applies a NAPE Test of Detail to a given evidence file."
    )
    parser.add_argument("--evidence", help="The evidence file to evaluate.")
    parser.add_argument(
        "--invoke",
        action="append",
        help="One JSON object containing test and evaluations for a single invocation.",
    )
    parser.add_argument(
        "--invoke-file",
        action="append",
        help="Path to one JSON object file containing test and evaluations for a single invocation.",
    )
    parser.add_argument(
        "--request-file",
        help="Path to one JSON request file containing evidence and tests, or - to read that full request from stdin.",
    )
    parser.add_argument(
        "--check-install",
        action="store_true",
        help="Check if the CLI is installed and working.",
    )
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    has_direct_invocations = bool(args.invoke or args.invoke_file)
    has_request_file = bool(args.request_file)

    if args.check_install and (
        args.evidence or has_direct_invocations or has_request_file
    ):
        parser.error(
            "--check-install cannot be combined with --evidence, --invoke, --invoke-file, or --request-file."
        )

    if (
        not args.check_install
        and not args.evidence
        and not has_direct_invocations
        and not has_request_file
    ):
        raise CliInvocationError(
            "cli_argument_error",
            "No evaluator invocation arguments were provided. Use --check-install, or provide --evidence with --invoke/--invoke-file, or use --request-file.",
        )

    if has_request_file and (args.evidence or has_direct_invocations):
        parser.error(
            "--request-file cannot be combined with --evidence, --invoke, or --invoke-file."
        )

    if has_direct_invocations and not args.evidence:
        parser.error("--evidence must be provided with --invoke or --invoke-file.")

    if args.evidence and not has_direct_invocations and not has_request_file:
        parser.error(
            "--evidence must be provided together with at least one --invoke or --invoke-file."
        )

    return args


def _candidate_test_paths(raw_tests):
    if not isinstance(raw_tests, list):
        return []
    test_paths = []
    for raw_test in raw_tests:
        if isinstance(raw_test, dict):
            test_path = raw_test.get("test")
            if isinstance(test_path, str) and test_path:
                test_paths.append(test_path)
    return test_paths


def _decode_json_string(raw_value: str, source_label: str):
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise CliInvocationError(
            "request_json_decode_error",
            f"Failed to decode {source_label} as JSON. {exc}",
        )


def _decode_json_file(path: str, source_label: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise CliInvocationError(
            "request_file_not_found",
            f"Unable to find {source_label}. {exc}",
        )
    except json.JSONDecodeError as exc:
        raise CliInvocationError(
            "request_json_decode_error",
            f"Failed to decode {source_label} as JSON. {exc}",
        )
    except Exception as exc:
        raise CliInvocationError(
            "request_file_load_error",
            f"Failed to load {source_label}. {exc}",
            stack_trace=traceback.format_exc(),
        )


def _decode_request_file(request_file: str):
    if request_file == "-":
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise CliInvocationError(
                "request_json_decode_error",
                f"Failed to decode stdin request JSON. {exc}",
            )
        except Exception as exc:
            raise CliInvocationError(
                "request_file_load_error",
                f"Failed to read stdin request JSON. {exc}",
                stack_trace=traceback.format_exc(),
            )
    return _decode_json_file(request_file, f"request file {request_file}")


def _decode_request_file_with_raw(request_file: str):
    try:
        if request_file == "-":
            raw = sys.stdin.buffer.read()
            source_label = "stdin request JSON"
        else:
            source_label = f"request file {request_file}"
            with open(request_file, "rb") as handle:
                raw = handle.read()
        return json.loads(raw.decode("utf-8")), raw
    except FileNotFoundError as exc:
        raise CliInvocationError(
            "request_file_not_found",
            f"Unable to find request file {request_file}. {exc}",
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        if request_file == "-":
            message = f"Failed to decode stdin request JSON. {exc}"
        else:
            message = f"Failed to decode {source_label} as JSON. {exc}"
        raise CliInvocationError(
            "request_json_decode_error",
            message,
        )
    except Exception as exc:
        raise CliInvocationError(
            "request_file_load_error",
            f"Failed to load {source_label}. {exc}",
            stack_trace=traceback.format_exc(),
        )


def build_request_from_args(args, request_packet=None):
    if args.request_file:
        if request_packet is None:
            request_packet = _decode_request_file(args.request_file)
        if not isinstance(request_packet, dict):
            raise CliInvocationError(
                "invalid_request_packet",
                "--request-file must decode to a top-level JSON object.",
            )
        try:
            return (
                EvaluateEvidenceRequest.builder()
                .evidence_path(request_packet.get("evidence"))
                .raw_tests(request_packet.get("tests"))
                .try_build()
            )
        except RequestValidationError as exc:
            raise CliInvocationError(
                exc.code,
                str(exc),
                evidence_file=request_packet.get("evidence")
                if isinstance(request_packet.get("evidence"), str)
                else None,
                affected_tests=_candidate_test_paths(request_packet.get("tests")),
            )

    raw_tests = []
    for raw_value in args.invoke or []:
        raw_tests.append(_decode_json_string(raw_value, "--invoke value"))
    for path in args.invoke_file or []:
        raw_tests.append(_decode_json_file(path, f"invoke file {path}"))

    try:
        return (
            EvaluateEvidenceRequest.builder()
            .evidence_path(args.evidence)
            .raw_tests(raw_tests)
            .try_build()
        )
    except RequestValidationError as exc:
        raise CliInvocationError(
            exc.code,
            str(exc),
            evidence_file=args.evidence,
            affected_tests=_candidate_test_paths(raw_tests),
        )


def run_cli(argv=None):
    try:
        args = parse_args(argv)

        if args.check_install:
            print("NAPE Evaluator CLI is installed and working.")
            return 0

        request_packet = None
        request_raw = None
        if args.request_file:
            request_packet, request_raw = _decode_request_file_with_raw(
                args.request_file
            )
            from nape_evaluator.v2 import (
                is_versioned_request,
                process_versioned_json,
                serialize_response,
            )

            if is_versioned_request(request_packet):
                response = process_versioned_json(request_raw)
                sys.stdout.buffer.write(serialize_response(response))
                sys.stdout.buffer.flush()
                return 0

        request = build_request_from_args(args, request_packet=request_packet)

        print(
            json.dumps(
                evaluate_request(
                    request,
                    DEFAULT_EVIDENCE_GATEWAY,
                    DEFAULT_TEST_OF_DETAIL_GATEWAY,
                ).to_cli_output()
            )
        )
        return 0
    except CliInvocationError as exc:
        print(json.dumps(exc.to_cli_output()))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                CliInvocationError(
                    "cli_unhandled_error",
                    f"Unexpected CLI failure. {exc}",
                    stack_trace=traceback.format_exc(),
                ).to_cli_output()
            )
        )
        return 0
