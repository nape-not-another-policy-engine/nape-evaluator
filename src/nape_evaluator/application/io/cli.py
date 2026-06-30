import argparse
import json
import sys

from nape_evaluator.application.driver.evidence_gateway import DEFAULT_EVIDENCE_GATEWAY
from nape_evaluator.application.driver.test_of_detail_gateway import (
    DEFAULT_TEST_OF_DETAIL_GATEWAY,
)
from nape_evaluator.domain.use_case_models import EvaluateEvidenceRequest
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
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check_install and (args.evidence or args.test):
        parser.error("--check-install cannot be combined with --evidence or --test.")

    if not args.check_install and not args.evidence and not args.test:
        parser.print_help(sys.stderr)
        raise SystemExit(2)

    if (args.evidence and not args.test) or (args.test and not args.evidence):
        parser.error("--evidence and --test must be provided together.")

    return args


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
                    test_paths=list(args.test),
                ),
                DEFAULT_EVIDENCE_GATEWAY,
                DEFAULT_TEST_OF_DETAIL_GATEWAY,
            ).to_cli_output()
        )
    )
    return 0
