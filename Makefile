.PHONY: build-release pip-install pip-uninstall pypi-publish clean docs-smoke release-validate-local release-validate-clean-install release-validate

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

pypi-publish:
	@echo "\n\033[1;96m Publishing the NAPE Evaluator to PyPI - [ $$PYPI_URL ] \033[0m\n"
	twine upload --verbose --repository-url $$PYPI_URL $(PYPI_DIST_DIR)/*
	@echo "\n\033[1;96m NAPE Evaluator - PyPI Publish - COMPLETE! \033[0m\n"

clean:
	@echo "\n\033[1;96m Cleaning all NAPE Evaluator files \033[0m\n"
	rm -rf $(BINARY_OUTPUT_DIR)
	rm -rf $(BUILD_OUTPUT_DIR)
	rm -rf build dist *.egg-info src/*.egg-info
	rm *.spec
	@echo "\n\033[1;96m NAPE Evaluator - All Cleaned Up - COMPLETE! \033[0m\n"

docs-smoke:
	@echo "\n\033[1;96m Running NAPE Evaluator docs smoke checks \033[0m\n"
	bash ./scripts/docs_smoke.sh
	@echo "\n\033[1;96m NAPE Evaluator - Docs Smoke - COMPLETE! \033[0m\n"

release-validate-local:
	@echo "\n\033[1;96m Running local release validation \033[0m\n"
	python3 -m unittest discover
	$(MAKE) docs-smoke
	EVALUATOR_USE_MAIN_PY=1 bash ./scripts/release_validation.sh
	@echo "\n\033[1;96m NAPE Evaluator - Local Release Validation - COMPLETE! \033[0m\n"

release-validate-clean-install:
	@echo "\n\033[1;96m Running clean-install release validation \033[0m\n"
	bash ./scripts/release_validation_clean_install.sh
	@echo "\n\033[1;96m NAPE Evaluator - Clean-Install Release Validation - COMPLETE! \033[0m\n"

release-validate: release-validate-local release-validate-clean-install
	@echo "\n\033[1;96m NAPE Evaluator - Full Release Validation - COMPLETE! \033[0m\n"
