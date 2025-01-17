# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export HOST ?= 0.0.0.0
export PORT ?= 8000
export MODEL ?= coffee-machine
export TEMPLATES_DIR ?= templates

# NOTE: Keep the 'help' target first, so that 'make' acts like 'make help'
.PHONY: help
help:
	@echo 'Note:'
	@echo ''
	@echo 'Run `dotenv run make ...` to consider environment'
	@echo 'variables from a .env file if existing'
	@echo ''
	@echo 'Append'
	@echo ''
	@echo '- `MODEL=/path/to/model.aird` to specify a model'
	@echo '- `TEMPLATES_DIR=/path/to/templates` to specify a templates dir'
	@echo ''
	@echo 'Available make targets:'
	@echo ''
	@echo '- run              -- Run the app in production mode'
	@echo '- dev              -- Run the app in development (reload) mode'
	@echo '- pre-commit-setup -- Setup the pre-commit environment'

.PHONY: run
run:
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" uvicorn \
		--host=$(HOST) \
		--port=$(PORT) \
		capella_model_explorer.main:app

.PHONY: dev
dev:
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" LIVE=1 uvicorn \
		--host=$(HOST) \
		--port=$(PORT) \
		--reload \
		--reload-exclude 'git_askpass.py' \
		--reload-include '*.css' \
		--reload-include '*.j2' \
		--reload-include '*.js' \
		--reload-include '*.py' \
		capella_model_explorer.main:app

.PHONY: pre-commit-setup
pre-commit-setup:
	npm install prettier prettier-plugin-jinja-template remark-parse
