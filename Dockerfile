# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

FROM python:3.12-slim-bookworm
USER root
WORKDIR /app
ENV HOME=/home
ENV PATH=$HOME/.local/bin:$PATH
ENV MODEL_ENTRYPOINT=/model
# Expose the port the app runs on
EXPOSE 8000

# install system pkgs {{{
RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
  curl \
  git \
  git-lfs \
  gir1.2-pango-1.0 \
  graphviz \
  libcairo2-dev \
  libgirepository1.0-dev \
  npm && \
  apt-get autoremove --yes && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
# }}}

# copy files {{{
COPY capella_model_explorer capella_model_explorer
COPY static static
COPY templates /templates
COPY pyproject.toml ./
COPY .git .git
COPY package*.json ./
# copy entrypoint.sh to root:
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
# }}}

# misc setup {{{
RUN git config --global --add safe.directory /model && \
  git config --global --add safe.directory /model/.git && \
  chmod -R 777 /app && \
  chmod -R a=rwX /home
# }}}

# Run as non-root user per default
USER 1000

# install uv {{{
RUN curl -Lo /tmp/install.sh https://astral.sh/uv/install.sh && \
  chmod +x /tmp/install.sh && \
  UV_NO_MODIFY_PATH=1 sh /tmp/install.sh && \
  rm /tmp/install.sh
# }}}

# install app incl. its cli and install elk.js {{{
RUN uv venv && \
  # install app
  uv pip install --no-cache-dir . && \
  rm -rf ./*.egg-info && \
  # Install elk.js automatically into a persistent local cache directory
  # in order to prepare the elk.js execution environment ahead of time.
  uv run python3 -c "from capellambse_context_diagrams import install_elk; install_elk()"
# }}}

# install Node pkgs and build the CSS {{{
RUN npm clean-install && \
  uv run python3 -m capella_model_explorer build && \
  rm -rf node_modules
# }}}

# clean up as root {{{
USER root
# keep /app read-only to the server process at runtime
RUN chown -R root:root /app && chmod -R a=rX /app
# }}}

# Ensure non-root user
USER 1000

ENTRYPOINT ["/entrypoint.sh"]
