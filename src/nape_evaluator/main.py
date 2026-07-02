"""Installed console-script entry point for nape-eval."""

from nape_evaluator.application.io.cli import run_cli


def main():
    raise SystemExit(run_cli())
