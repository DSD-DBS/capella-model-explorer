# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import pathlib
import subprocess

import capellambse
from capella_diff_tools import compare, report, types
from capellambse.filehandler import git, local

logger = logging.getLogger(__name__)
NUM_COMMITS = "20"


def init_model(model: capellambse.MelodyModel):
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
        return {"error": "Not a git repo"}, model_data
    return path, model_data


def populate_commits(model: capellambse.MelodyModel):
    result, _ = init_model(model)
    if "error" in result:
        return result
    commits = get_commit_hashes(result)
    return commits


def get_data(model: capellambse.MelodyModel, head: str, prev: str):
    path, model_data = init_model(model)
    path = pathlib.Path(path).resolve()
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
    report._compute_diff_stats(data)
    model_data = report._traverse_and_diff(data)
    return model_data


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
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", revision],
            cwd=repo_path,
            encoding="utf-8",
        ).strip()
    except subprocess.CalledProcessError:
        tag = None
    return {
        "hash": revision,
        "revision": revision,
        "author": author,
        "date": datetime.datetime.fromisoformat(date_str),
        "description": description.rstrip(),
        "tag": tag,
    }


def get_commit_hashes(path: str):
    commit_hashes = subprocess.check_output(
        ["git", "log", "-n", NUM_COMMITS, "--format=%H"],
        cwd=path,
        encoding="utf-8",
    ).splitlines()
    commits = [_get_revision_info(path, c) for c in commit_hashes]
    return commits
