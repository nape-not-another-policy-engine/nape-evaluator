import json
import argparse
import importlib.util
import sys


def main():
    try:
        parser = argparse.ArgumentParser(description='Applies a NAPE Control Action Test to a given evidence file.')
        parser.add_argument('--evidence', help='The evidence file to evaluate.')
        parser.add_argument('--test', help='The Control Acton test file.')
        parser.add_argument('--check-install', action='store_true', help='Check if the CLI is installed and working.')
        args = parser.parse_args()

        # Custom validation
        if (args.evidence and not args.test) or (args.test and not args.evidence):
            parser.error("--evidence and --test must be provided together.")

        if args.check_install:
            print("NAPE Evaluator CLI is installed and working.")
            sys.exit(0)

        # Read the text file
        with open(args.evidence, 'r') as f:
            text = f.readlines()

        # Dynamically import the Control Action file
        spec = importlib.util.spec_from_file_location("module.name", args.test)
        action_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(action_module)

        # Call the evaluate function and print the result
        outcome, reason = action_module.evaluate(text)
        result = {"outcome": outcome, "reason": reason}
        print(json.dumps(result))

    except FileNotFoundError as e:
        result = {"outcome": "error", "reason": "Unable to find the file(s) for evaluation. " + str(e)}
        print(json.dumps(result))
    except ImportError as e:
        result = {"outcome": "error", "reason": "Failed to import the necessary files. " + str(e)}
        print(json.dumps(result))
    except Exception as e:
        result = {"outcome": "error", "reason": "Failed to execute the evidence evaluation. " + str(e)}
        print(json.dumps(result))


if __name__ == '__main__':
    main()
