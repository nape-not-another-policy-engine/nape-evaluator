.PHONY: build-release clean install

PROJECT_NAME = nape
BINARY_OUTPUT_DIR = binary-output
BUILD_OUTPUT_DIR = build-output
PYPI_DIST_DIR = $(BUILD_OUTPUT_DIR)/dist

build-release:
	@echo "\n\033[1;96m Starting the Release Build \033[0m\n"
	@if [ -d "$(BUILD_OUTPUT_DIR)" ]; then rm -rf $(BUILD_OUTPUT_DIR)/*; else mkdir -p $(BUILD_OUTPUT_DIR); fi
	python setup.py sdist --dist-dir $(PYPI_DIST_DIR)
	python setup.py bdist_wheel --dist-dir $(PYPI_DIST_DIR)
	mv nape.egg-info $(BUILD_OUTPUT_DIR)
	@echo "\n\033[1;96m NAPE Evaluator - Release Build COMPLETE! \033[0m\n"

pip-install: build-release
	@echo "\n\033[1;96m Installing the NAPE Evaluator with PIP \033[0m\n"
	pip install $(shell ls $(PYPI_DIST_DIR)/*.whl)
	@echo "\n\033[1;96m NAPE Evaluator - PIP Installation - COMPLETE! \033[0m\n"

pip-uninstall:
	@echo "\n\033[1;96m Uninstalling the NAPE Evaluator with PIP \033[0m\n"
	pip uninstall -y $(PROJECT_NAME)
	@echo "\n\033[1;96m NAPE Evaluator - PIP Uninstallation - COMPLETE! \033[0m\n"

clean:
	@echo "\n\033[1;96m Cleaning all NAPE Evaluator files \033[0m\n"
	rm -rf $(BINARY_OUTPUT_DIR)
	rm -rf $(BUILD_OUTPUT_DIR)
	rm -rf build dist *.egg-info
	rm *.spec
	@echo "\n\033[1;96m NAPE Evaluator - All Cleaned Up - COMPLETE! \033[0m\n"