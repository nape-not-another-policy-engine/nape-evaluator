# Test Suite Structure

This folder contains both evaluator contract tests and executable authoring examples.

## High-Level Split

- root `tests/test_*.py` files cover evaluator behavior, gateways, request validation, output shaping, and CLI behavior
- `tests/json/`, `tests/xml/`, `tests/yaml/`, `tests/text/`, and `tests/pdf/` hold copyable format-specific authoring examples plus focused tests that prove those examples use caller-owned evaluation inputs
- `tests/v1_baseline/` is historical comparison material
- `tests/manual/` contains manual smoke entry points

## Format Example Model

Each format-family example tree uses the same model when practical:

- `evidence/`
- `test_of_detail/`
- `test_pattern_library.py`

The intent is:

- `evidence/` holds example evidence files where stable artifacts are practical
- `test_of_detail/` holds copyable Python tests an author can study or adapt
- `test_pattern_library.py` proves those fixtures work and actually honor caller-owned `evaluations`

## Why PDF Uses A Controlled Seam

PDF authoring examples are still important, but PDF artifact generation can easily dominate the maintenance cost of a small example suite.

For that reason, the PDF example path focuses on:

- a real copyable test-of-detail fixture
- a focused automated test that controls the text-extraction seam

That keeps the suite centered on authoring patterns rather than binary artifact churn.
