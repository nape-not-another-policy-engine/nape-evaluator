import argparse
import json
import sys

from nape_evaluator.application.driver.evidence_gateway import DEFAULT_EVIDENCE_GATEWAY
from nape_evaluator.application.driver.test_of_detail_gateway import (
    DEFAULT_TEST_OF_DETAIL_GATEWAY,
)
from nape_evaluator.domain.use_case_models import (
    EvaluateEvidenceRequest,
    TestInvocationRequest,
)
from nape_evaluator.domain.use_cases import evaluate_request


def build_parser():
    parser = argparse.ArgumentParser(
        description="Applies a NAPE Test of Detail to a given evidence file."
    )
    parser.add_argument("--evidence", help="The evidence file to evaluate.")
    parser.add_argument(
        "--test",
        action="append",
        help="A Test of Detail file. Repeat this argument to evaluate multiple tests against the same evidence.",
    )
    parser.add_argument(
        "--check-install",
        action="store_true",
        help="Check if the CLI is installed and working.",
    )
    parser.add_argument(
        "--test-parameters-file",
        action="append",
        help="Path to a JSON object file containing caller-supplied parameters for one test. Repeat once per --test in the same order.",
    )
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check_install and (args.evidence or args.test or args.test_parameters_file):
        parser.error(
            "--check-install cannot be combined with --evidence, --test, or --test-parameters-file."
        )

    if (
        not args.check_install
        and not args.evidence
        and not args.test
        and not args.test_parameters_file
    ):
        parser.print_help(sys.stderr)
        raise SystemExit(2)

    if (
        (args.evidence and not args.test)
        or (args.test and not args.evidence)
        or (args.test_parameters_file and (not args.evidence or not args.test))
    ):
        parser.error("--evidence and --test must be provided together.")

    if args.test_parameters_file and len(args.test_parameters_file) != len(args.test):
        parser.error(
            "--test-parameters-file must be omitted or repeated once per --test."
        )

    return args


def load_test_parameters_file(test_path, test_parameters_source):
    try:
        with open(test_parameters_source, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        return TestInvocationRequest.blocked(
            test_path,
            "test_parameter_file_not_found",
            "Unable to find the test parameter file for evaluation. " + str(exc),
            test_parameters_source=test_parameters_source,
        )
    except json.JSONDecodeError as exc:
        return TestInvocationRequest.blocked(
            test_path,
            "test_parameter_decode_error",
            "Failed to decode the test parameter file as JSON. " + str(exc),
            test_parameters_source=test_parameters_source,
        )
    except Exception as exc:
        return TestInvocationRequest.blocked(
            test_path,
            "test_parameter_load_error",
            "Failed to load the test parameter file. " + str(exc),
            test_parameters_source=test_parameters_source,
        )

    if not isinstance(data, dict):
        return TestInvocationRequest.blocked(
            test_path,
            "test_parameter_shape_error",
            "Test parameter input must be a top-level JSON object.",
            test_parameters_source=test_parameters_source,
        )

    return TestInvocationRequest.ready(
        test_path,
        data,
        test_parameters_source=test_parameters_source,
    )


def build_test_invocations(test_files, test_parameter_files):
    if not test_parameter_files:
        return [TestInvocationRequest.ready(test_path, {}) for test_path in test_files]

    invocations = []
    for test_path, test_parameters_source in zip(test_files, test_parameter_files):
        invocations.append(load_test_parameters_file(test_path, test_parameters_source))
    return invocations


def run_cli(argv=None):
    args = parse_args(argv)

    if args.check_install:
        print("NAPE Evaluator CLI is installed and working.")
        return 0

    print(
        json.dumps(
            evaluate_request(
                EvaluateEvidenceRequest(
                    evidence_path=args.evidence,
                    test_invocations=build_test_invocations(
                        list(args.test),
                        list(args.test_parameters_file) if args.test_parameters_file else [],
                    ),
                ),
                DEFAULT_EVIDENCE_GATEWAY,
                DEFAULT_TEST_OF_DETAIL_GATEWAY,
            ).to_cli_output()
        )
    )
    return 0
