# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import hashlib
import logging
import os
import pathlib

import capellambse.model

import capella_model_explorer.constants as c


def compute_file_hash(file_path: str):
    """Compute a hash for the given file."""
    if not pathlib.Path(file_path).exists():
        return ""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def jsfromfile(jsfilepath: os.PathLike | str) -> str:
    return pathlib.Path(jsfilepath).read_text(encoding="utf8")


def model_id(model: capellambse.model.MelodyModel) -> str:
    separator = "~~"
    uuid = model.uuid
    branch = model.info.resources["\x00"].branch
    rev_hash = model.info.resources["\x00"].rev_hash
    components = []
    for component in (uuid, branch, rev_hash):
        if component:
            components.append(component)
    return separator.join(components)


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        max_levelname_len = 8
        reset_seq = "\033[0m"
        levelname = record.levelname
        formatted_level_name = levelname
        while len(formatted_level_name) < max_levelname_len:
            formatted_level_name += " "
        msg = record.msg

        if levelname in c.LOGGING_COLORS:
            levelname_color = (
                c.LOGGING_COLORS[levelname] + formatted_level_name + reset_seq
            )
            msg_color = c.LOGGING_COLORS[levelname] + msg + reset_seq
        else:
            levelname_color = levelname
            msg_color = msg

        record.levelname = levelname_color
        record.msg = msg_color

        return super().format(record)


def setup_logging(logger: logging.Logger):
    formatter = ColoredFormatter(
        "%(asctime)s.%(msecs)03d|%(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d|%H:%M:%S",
    )
    for handler in logger.handlers:
        handler.setFormatter(formatter)
