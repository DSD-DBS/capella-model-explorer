# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

FROM python:3.12-slim-bookworm
WORKDIR /app
USER root
# install system pkgs {{{
RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
  curl \
  git \
  git-lfs \
  libgirepository1.0-dev \
  libcairo2-dev \
  gir1.2-pango-1.0 \
  graphviz \
  make && \
  rm -rf /var/lib/apt/lists/*
# }}}
# copy needed app assets {{{
COPY capella_model_explorer capella_model_explorer
COPY static static
COPY templates templates
COPY Makefile pyproject.toml ./
COPY .git .git
COPY entrypoint.sh /
# }}}
# Expose the port the app runs on
EXPOSE 8000
ENV HOME=/home
RUN chmod +x /entrypoint.sh
ENV MODEL_ENTRYPOINT=/model

RUN git config --global --add safe.directory /model && \
  git config --global --add safe.directory /model/.git && \
  chmod -R 777 /app && \
  chmod -R 777 /home

# Run as non-root user per default
USER 1000

# install uv {{{
RUN curl -Lo /tmp/install.sh https://astral.sh/uv/install.sh && \
  chmod +x /tmp/install.sh && \
  UV_NO_MODIFY_PATH=1 sh /tmp/install.sh && \
  rm /tmp/install.sh
# }}}

RUN $HOME/.local/bin/uv venv && \
  # install app
  $HOME/.local/bin/uv pip install --no-cache-dir . && \
  # Install elk.js automatically into a persistent local cache directory
  # in order to prepare the elk.js execution environment ahead of time.
  $HOME/.local/bin/uv run python3 -c "from capellambse_context_diagrams import install_elk; install_elk()"
ENTRYPOINT ["/entrypoint.sh"]
