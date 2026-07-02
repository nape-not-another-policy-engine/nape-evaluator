import argparse
import json
import sys

from nape_evaluator.application.driver.evidence_gateway import DEFAULT_EVIDENCE_GATEWAY
from nape_evaluator.application.driver.test_of_detail_gateway import (
    DEFAULT_TEST_OF_DETAIL_GATEWAY,
)
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    RequestValidationError,
)
from nape_evaluator.domain.use_cases import evaluate_request


def build_parser():
    parser = argparse.ArgumentParser(
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
        parser.print_help(sys.stderr)
        raise SystemExit(2)

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


def _raise_cli_error(message: str):
    build_parser().error(message)


def _decode_json_string(raw_value: str, source_label: str):
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        _raise_cli_error(f"Failed to decode {source_label} as JSON. {exc}")


def _decode_json_file(path: str, source_label: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        _raise_cli_error(f"Unable to find {source_label}. {exc}")
    except json.JSONDecodeError as exc:
        _raise_cli_error(f"Failed to decode {source_label} as JSON. {exc}")
    except Exception as exc:
        _raise_cli_error(f"Failed to load {source_label}. {exc}")


def _decode_request_file(request_file: str):
    if request_file == "-":
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            _raise_cli_error(f"Failed to decode stdin request JSON. {exc}")
        except Exception as exc:
            _raise_cli_error(f"Failed to read stdin request JSON. {exc}")
    return _decode_json_file(request_file, f"request file {request_file}")


def build_request_from_args(args):
    try:
        if args.request_file:
            request_packet = _decode_request_file(args.request_file)
            if not isinstance(request_packet, dict):
                _raise_cli_error("--request-file must decode to a top-level JSON object.")
            return (
                EvaluateEvidenceRequest.builder()
                .evidence_path(request_packet.get("evidence"))
                .raw_tests(request_packet.get("tests"))
                .try_build()
            )

        raw_tests = []
        for raw_value in args.invoke or []:
            raw_tests.append(_decode_json_string(raw_value, "--invoke value"))
        for path in args.invoke_file or []:
            raw_tests.append(_decode_json_file(path, f"invoke file {path}"))

        return (
            EvaluateEvidenceRequest.builder()
            .evidence_path(args.evidence)
            .raw_tests(raw_tests)
            .try_build()
        )
    except RequestValidationError as exc:
        _raise_cli_error(str(exc))


def run_cli(argv=None):
    args = parse_args(argv)

    if args.check_install:
        print("NAPE Evaluator CLI is installed and working.")
        return 0

    request = build_request_from_args(args)

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
