import json
import argparse
import importlib.util
import sys
import os
import xml.etree.ElementTree as ET
import yaml
import PyPDF2


def load_evidence(evidence_path):
    """Load evidence into the Python type expected for its extension."""
    _, file_extension = os.path.splitext(evidence_path)
    file_extension = file_extension.lower()

    try:
        if file_extension in [".txt"]:
            with open(evidence_path, "r", encoding="utf-8") as f:
                return f.readlines()
        if file_extension in [".json"]:
            with open(evidence_path, "r", encoding="utf-8") as f:
                return json.load(f)
        if file_extension in [".xml"]:
            tree = ET.parse(evidence_path)
            return tree.getroot()
        if file_extension in [".yaml", ".yml"]:
            with open(evidence_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        if file_extension in [".pdf"]:
            with open(evidence_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text.splitlines()

        # Treat unknown file types as text for backward compatibility.
        with open(evidence_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        raise ValueError(f"Error loading evidence: {e}")


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Applies a NAPE Test of Detail to a given evidence file."
        )
        parser.add_argument("--evidence", help="The evidence file to evaluate.")
        parser.add_argument("--test", help="The Test of Detail file.")
        parser.add_argument(
            "--check-install",
            action="store_true",
            help="Check if the CLI is installed and working.",
        )
        args = parser.parse_args()

        if (args.evidence and not args.test) or (args.test and not args.evidence):
            parser.error("--evidence and --test must be provided together.")

        if args.check_install:
            print("NAPE Evaluator CLI is installed and working.")
            sys.exit(0)

        evidence_data = load_evidence(args.evidence)

        spec = importlib.util.spec_from_file_location("module.name", args.test)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load the test file: {args.test}")
        action_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(action_module)

        outcome, reason = action_module.evaluate(evidence_data)
        result = {"outcome": outcome, "reason": reason}
        print(json.dumps(result))

    except FileNotFoundError as e:
        result = {"outcome": "error", "reason": "Unable to find the file(s) for evaluation. " + str(e)}
        print(json.dumps(result))
    except ImportError as e:
        result = {"outcome": "error", "reason": "Failed to import the necessary files. " + str(e)}
        print(json.dumps(result))
    except ValueError as e:
        result = {"outcome": "error", "reason": str(e)}
        print(json.dumps(result))
    except Exception as e:
        result = {"outcome": "error", "reason": "Failed to execute the evidence evaluation. " + str(e)}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
