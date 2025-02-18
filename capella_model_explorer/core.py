# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import hashlib
import logging
import pathlib

import capella_model_explorer.constants as c


def compute_file_hash(file_path: str):
    """Compute a hash for the given file."""
    if not pathlib.Path(file_path).exists():
        return ""
    hasher = hashlib.blake2b(digest_size=9, usedforsecurity=False)
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8")


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        reset_seq = "\033[0m"
        levelname = record.levelname
        msg = record.msg
        if levelname in c.LOGGING_COLORS:
            levelname_colored = (
                f"{c.LOGGING_COLORS[levelname]}{levelname:8}{reset_seq}"
            )
            msg_color = c.LOGGING_COLORS[levelname] + msg + reset_seq
        else:
            levelname_colored = levelname
            msg_color = msg
        record.levelname = levelname_colored
        record.msg = msg_color
        return super().format(record)


def setup_logging(logger: logging.Logger):
    logging.getLogger("uvicorn").setLevel("INFO")
    formatter = ColoredFormatter(
        "%(asctime)s.%(msecs)03d|%(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d|%H:%M:%S",
    )
    for handler in logger.handlers:
        handler.setFormatter(formatter)
