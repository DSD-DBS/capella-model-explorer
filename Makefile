# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CAPELLA_MODEL_EXPLORER_HOST_IP ?= 0.0.0.0
CAPELLA_MODEL_EXPLORER_PORT ?= 8000
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
	@echo '- run    -- Run the application in production mode'
	@echo '- dev    -- Run the application in development (reload) mode'

.PHONY: run
run:
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" LIVE_RELOAD=0 uvicorn \
		--host=$(CAPELLA_MODEL_EXPLORER_HOST_IP) \
		--port=$(CAPELLA_MODEL_EXPLORER_PORT) \
		capella_model_explorer.main:app

.PHONY: dev
dev:
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" LIVE_RELOAD=1 uvicorn \
		--host=$(CAPELLA_MODEL_EXPLORER_HOST_IP) \
		--port=$(CAPELLA_MODEL_EXPLORER_PORT) \
		--reload \
		capella_model_explorer.main:app
