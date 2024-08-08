.PHONY: build dist clean install

OUTPUT_DIR = build-output
INSTALL_DIR = /usr/local/bin
CLI_NAME = nape-eval

build:
	@echo "\n\033[1;96m Starting the Release Build \033[0m\n"
	@if [ -d "$(OUTPUT_DIR)" ]; then rm -rf $(OUTPUT_DIR)/*; else mkdir -p $(OUTPUT_DIR); fi
	python setup.py sdist bdist_wheel --dist-dir $(OUTPUT_DIR)
	mv build $(OUTPUT_DIR)
	mv dist $(OUTPUT_DIR)
	mv nape_eval.egg-info $(OUTPUT_DIR)
	@echo "\n\033[1;96m NAPE Evaluator - Release Build COMPLETE! \033[0m\n"

dist: build
	@echo "\n\033[1;96m Creating the NAPE Evaluator distribution \033[0m\n"
	twine upload dist/*
	@echo "\n\033[1;96m NAPE Evaluator - Distribution - COMPLETE! \033[0m\n"


# for Install, have folks pip install the .whl file in the build-output` directory
#install: build
#	@echo "\n\033[1;96m Installing the NAPE Evaluator into '$(INSTALL_DIR)' \033[0m\n"
#	pip install
#	@echo "\n\033[1;96m NAPE Evaluator - Installation - COMPLETE! '$(INSTALL_DIR)' \033[0m\n"
#local-install: build
#	@echo "\n\033[1;96m Installing the NAPE Evaluator intto the local environment '$(INSTALL_DIR)' \033[0m\n"
#	pip install .
#	@echo "\n\033[1;96m NAPE Evaluator - Local Environment Installation - COMPLETE! '$(INSTALL_DIR)' \033[0m\n"

clean:
	@echo "\n\033[1;96m Cleaning all NAPE Evaluator files \033[0m\n"
	rm -rf $(OUTPUT_DIR)
	rm -rf build dist *.egg-info
	@echo "\n\033[1;96m NAPE Evaluator - All Cleaned Up - COMPLETE! \033[0m\n"