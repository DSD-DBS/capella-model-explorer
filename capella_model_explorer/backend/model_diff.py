# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import copy
import datetime
import logging
import subprocess

import capellambse
from capella_diff_tools import __main__ as diff
from capella_diff_tools import compare, report, types
from capellambse.filehandler import git, local

logger = logging.getLogger(__name__)


def get_data(model: capellambse.MelodyModel):
    file_handler = model.resources["\x00"]
    path = str(file_handler.path)
    model_data: dict = {
        "metadata": {"model": {"path": path, "entrypoint": None}},
        "diagrams": {
            "created": {},
            "modified": {},
            "deleted": {},
        },
        "objects": {
            "created": {},
            "modified": {},
            "deleted": {},
        },
    }

    if isinstance(file_handler, git.GitFileHandler):
        path = str(file_handler.cache_dir)
    elif (
        isinstance(file_handler, local.LocalFileHandler)
        and file_handler.rootdir.joinpath(".git").is_dir()
    ):
        pass
    else:
        logger.warning("Cannot create a diff: Not a git repo")
        return model_data

    commit_hashes = (
        subprocess.check_output(
            ["git", "log", "-n", "7", "--format=%H"],
            cwd=path,
            encoding="utf-8",
        )
        .strip()
        .split("\n")
    )

    if len(commit_hashes) > 1:
        head = commit_hashes[0]
        prev = commit_hashes[6]
        old_model = capellambse.MelodyModel(path=f"git+{path}", revision=prev)

        metadata: types.Metadata = {
            "model": {"path": path, "entrypoint": None},
            "old_revision": _get_revision_info(path, prev),
            "new_revision": _get_revision_info(path, head),
        }

        diagrams = compare.compare_all_diagrams(old_model, model)
        objects = compare.compare_all_objects(old_model, model)
        data: types.ChangeSummaryDocument = {
            "metadata": metadata,
            "diagrams": diagrams,
            "objects": objects,
        }
        data = copy.deepcopy(data)
        report._compute_diff_stats(data)
        model_data = report._traverse_and_diff(data)
        return model_data
    else:
        raise ValueError("Not enought commits in the repository to compare")


def _get_revision_info(
    repo_path: str,
    revision: str,
) -> types.RevisionInfo:
    """Return the revision info of the given model."""
    author, date_str, description = (
        subprocess.check_output(
            ["git", "log", "-1", "--format=%aN%x00%aI%x00%B", revision],
            cwd=repo_path,
            encoding="utf-8",
        )
        .strip()
        .split("\x00")
    )
    return {
        "hash": revision,
        "revision": revision,
        "author": author,
        "date": datetime.datetime.fromisoformat(date_str),
        "description": description.rstrip(),
    }
