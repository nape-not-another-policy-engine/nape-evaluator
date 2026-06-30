import importlib.util


class PythonTestOfDetailGateway:
    def load_test_of_detail(self, test_path):
        spec = importlib.util.spec_from_file_location("module.name", test_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load the test file: {test_path}")
        action_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(action_module)
        return action_module


DEFAULT_TEST_OF_DETAIL_GATEWAY = PythonTestOfDetailGateway()
