# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CAPELLA_MODEL_EXPLORER_HOST_IP ?= 0.0.0.0
CAPELLA_MODEL_EXPLORER_PORT ?= 8000
export MODEL ?= coffee-machine
export TEMPLATES_DIR ?= templates

# NOTE: Keep the 'help' target first, so that 'make' acts like 'make help'
.PHONY: help
help:
	@echo 'Available make targets:'
	@echo ''
	@echo 'Note:  `UV_ENV_FILE=.env uv run make ...` or `dotenv run make ...`'
	@echo 'can be used to run make with environment variables from a .env file'
	@echo ''
	@echo '    run MODEL=/some/model.aird'
	@echo '                    -- Run the app in production mode with a model'
	@echo '    dev-backend     -- Run the backend in development mode'
	@echo '    dev-frontend    -- Run the frontend in development mode'
	@echo '    build-frontend  -- (Re-)Build the prod frontend files'
	@echo '    storybook       -- Run storybook for frontend development'
	@echo '    clean-frontend  -- Clean out all built/installed frontend files'

.PHONY: run
run: frontend/dist/static/env.js
	sed -i -e "s|__ROUTE_PREFIX__||g" frontend/dist/static/env.js
	MODE=production python frontend/fetch-version.py
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" uvicorn \
		--host=$(CAPELLA_MODEL_EXPLORER_HOST_IP) \
		--port=$(CAPELLA_MODEL_EXPLORER_PORT) \
		capella_model_explorer.backend.main:app

.PHONY: build-frontend
build-frontend: frontend/node_modules
	cd frontend && npm run build

.PHONY: dev-backend
dev-backend:
	sed -i -e "s|__ROUTE_PREFIX__||g" frontend/dist/static/env.js
	MODE=production python frontend/fetch-version.py
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODEL="$$MODEL" TEMPLATES_DIR="$$TEMPLATES_DIR" uvicorn \
		--host=$(CAPELLA_MODEL_EXPLORER_HOST_IP) \
		--port=$(CAPELLA_MODEL_EXPLORER_PORT) \
		--reload \
		capella_model_explorer.backend.main:app

.PHONY: dev-frontend
dev-frontend: frontend/node_modules
	sed -i -e "s|__ROUTE_PREFIX__||g" frontend/dist/static/env.js
	python frontend/fetch-version.py
	cd frontend && npm run dev

.PHONY: storybook
storybook: frontend/node_modules
	cd frontend && npm run storybook

.PHONY: clean-frontend
clean-frontend:
	cd frontend && rm -rf dist node_modules

frontend/dist/static/env.js: frontend/node_modules
	cd frontend && npm run build
	touch -c frontend/dist/static/env.js

frontend/node_modules: frontend/package.json frontend/package-lock.json
	cd frontend && npm install
	touch -c frontend/node_modules
