import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nape_evaluator.application.io.cli import run_cli


def main():
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
