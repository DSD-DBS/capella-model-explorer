# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CAPELLA_MODEL_EXPLORER_HOST_IP ?= 127.0.0.1
CAPELLA_MODEL_EXPLORER_PORT ?= 8000
MODEL ?= coffee-machine

# NOTE: Keep the 'help' target first, so that 'make' acts like 'make help'
.PHONY: help
help:
	@echo 'Available make targets:'
	@echo ''
	@echo '    run MODEL=/some/model.aird'
	@echo '                    -- Run the backend with a model'
	@echo '    build-frontend  -- (Re-)Build the prod frontend files'
	@echo '    dev-frontend    -- Run the frontend in dev mode'
	@echo '    storybook       -- Run storybook for frontend development'
	@echo '    clean-frontend  -- Clean out all built/installed frontend files'

.PHONY: run
run: frontend/dist/static/env.js
	sed -i "s|__ROUTE_PREFIX__||g" frontend/dist/static/env.js
	MODE=production python frontend/fetch-version.py
	python -c "from capellambse_context_diagrams import install_elk; install_elk()"
	MODE=production python -m capella_model_explorer.backend "$$MODEL" ./templates

.PHONY: build-frontend
build-frontend: frontend/node_modules
	cd frontend && npm run build

.PHONY: dev-frontend
dev-frontend: frontend/node_modules
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
