# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import contextlib
import copy
import hashlib
import logging
import pathlib

import logfmter

ACCESS_LOGGER = "uvicorn.access"


def compute_file_hash(file_path: str):
    """Compute a hash for the given file."""
    if not pathlib.Path(file_path).exists():
        return ""
    hasher = hashlib.blake2b(digest_size=9, usedforsecurity=False)
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8")


class Logfmter(logfmter.Logfmter):
    def format(self, record: logging.LogRecord) -> str:
        record = copy.copy(record)

        if record.name == ACCESS_LOGGER:
            assert record.args is not None
            (
                record.client_addr,
                record.method,
                record.path,
                record.http_version,
                record.status_code,
            ) = record.args
            record.msg = "Request completed"
            record.args = ()

        with contextlib.suppress(AttributeError):
            del record.color_message  # type: ignore[attr-defined]

        return super().format(record)


class SuppressWebsocketNoise(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not (
            record.name == "uvicorn.error" and hasattr(record, "websocket")
        )
