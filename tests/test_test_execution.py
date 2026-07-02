import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from nape_evaluator.application.driver.test_of_detail_gateway import (
    DEFAULT_TEST_OF_DETAIL_GATEWAY,
    PythonTestOfDetailGateway,
)


class TestTestExecution(unittest.TestCase):
    def test_default_gateway_is_python_test_of_detail_gateway(self):
        self.assertIsInstance(DEFAULT_TEST_OF_DETAIL_GATEWAY, PythonTestOfDetailGateway)

    def test_gateway_exposes_load_test_of_detail(self):
        gateway = PythonTestOfDetailGateway()
        self.assertTrue(callable(gateway.load_test_of_detail))

    def test_load_test_of_detail_returns_module_with_evaluate(self):
        gateway = PythonTestOfDetailGateway()

        with TemporaryDirectory() as tmp_dir:
            test_path = Path(tmp_dir) / "test_of_detail.py"
            test_path.write_text(
                "\n".join(
                    [
                        "def evaluate(evidence, evaluations, metadata):",
                        "    return {'conclusion': 'true', 'facts': [], 'reason': 'ok'}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            module = gateway.load_test_of_detail(str(test_path))

        self.assertTrue(callable(module.evaluate))
        self.assertEqual(
            module.evaluate({}, [], {}),
            {"conclusion": "true", "facts": [], "reason": "ok"},
        )

    def test_load_test_of_detail_raises_file_not_found_for_missing_path(self):
        gateway = PythonTestOfDetailGateway()

        with self.assertRaises(FileNotFoundError):
            gateway.load_test_of_detail("./does-not-exist.py")

    def test_load_test_of_detail_raises_import_error_when_spec_cannot_be_built(self):
        gateway = PythonTestOfDetailGateway()

        with patch(
            "nape_evaluator.application.driver.test_of_detail_gateway.importlib.util.spec_from_file_location",
            return_value=None,
        ):
            with self.assertRaises(ImportError):
                gateway.load_test_of_detail("./bad-test.py")

    def test_load_test_of_detail_raises_import_error_when_spec_has_no_loader(self):
        gateway = PythonTestOfDetailGateway()

        with patch(
            "nape_evaluator.application.driver.test_of_detail_gateway.importlib.util.spec_from_file_location",
            return_value=type("Spec", (), {"loader": None})(),
        ):
            with self.assertRaises(ImportError):
                gateway.load_test_of_detail("./bad-test.py")
