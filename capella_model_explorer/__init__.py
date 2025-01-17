# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""The capella_model_explorer package."""

from __future__ import annotations

from importlib import metadata

try:
    __version__ = metadata.version("capella_model_explorer")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"
del metadata
