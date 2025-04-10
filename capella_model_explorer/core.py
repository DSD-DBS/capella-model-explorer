# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import hashlib
import pathlib


def compute_file_hash(file_path: str):
    """Compute a hash for the given file."""
    if not pathlib.Path(file_path).exists():
        return ""
    hasher = hashlib.blake2b(digest_size=9, usedforsecurity=False)
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8")
