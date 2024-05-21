# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Build frontend
FROM node:20 as build-frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY ./capella_model_explorer ./capella_model_explorer
COPY ./pyproject.toml ./
COPY ./.git ./.git

USER root

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    git \
    git-lfs \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    graphviz \
    nodejs \
    npm && \
    rm -rf /var/lib/apt/lists/*

RUN pip install .
COPY --from=build-frontend /app/dist/ ./frontend/dist/

# Expose the port the app runs in
EXPOSE 8000

COPY ./templates /views

# Cache directory has to be writable
RUN chmod -R 777 /home
ENV HOME=/home

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV MODEL_ENTRYPOINT=/model
RUN chmod -R 777 ./frontend/dist/

# Run script to get software version
COPY frontend/fetch-version.py ./frontend/
RUN python frontend/fetch-version.py

# Run as non-root user per default
USER 1001

# Pre-install npm dependencies for context diagrams
RUN python -c "from capellambse_context_diagrams import _elkjs; _elkjs._install_required_npm_pkg_versions()"

ENTRYPOINT ["/entrypoint.sh"]
