# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import argparse
import subprocess
from pathlib import Path

import capellambse
from capella_diff_tools import __main__ as capella_diff_tools


def model_diff():
    data: dict = {
        "created": {},
        "modified": {},
        "deleted": {},
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)
    p = parser.parse_args()
    model_path = p.file_path
    model_dict = {"path": capella_diff_tools._ensure_git(model_path)}
    if model_dict["path"]:
        print(f"The model at {model_path} is inside a Git repository.")
        commit_hashes_result = subprocess.run(
            ["git", "log", "--format=%H"],
            cwd=model_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        commit_hashes = commit_hashes_result.stdout.strip().split("\n")
        if len(commit_hashes) > 1:

            old_model = capellambse.MelodyModel(
                **model_dict, revision=commit_hashes[7]
            )
            new_model = capellambse.MelodyModel(
                **model_dict, revision=commit_hashes[0]
            )
            objects = capella_diff_tools.compare.compare_all_objects(
                old_model, new_model
            )
            diagrams = capella_diff_tools.compare.compare_all_diagrams(
                old_model, new_model
            )
            print(objects)
            transform_object_dict(objects)
            data = {
                "Diagrams": transform_diagram_dict(diagrams),
                "Objects": transform_object_dict(objects),
            }
            return data
        else:
            pass

    return data


def transform_diagram_dict(dict):
    modified: list = []
    created: list = []
    deleted: list = []
    traverse_diagrams(dict, created, modified, deleted)
    created_dict = [
        {"name": item["display_name"], "uuid": item["uuid"]}
        for item in created
    ]
    modified_dict = [
        {"name": item["display_name"], "uuid": item["uuid"]}
        for item in modified
    ]
    deleted_dict = [
        {"name": item["display_name"], "uuid": item["uuid"]}
        for item in deleted
    ]
    diff_dict = {
        "Created": created_dict,
        "Modified": modified_dict,
        "Deleted": deleted_dict,
    }
    return diff_dict


def traverse_diagrams(node, created, modified, deleted):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "modified":
                modified.extend(value)
            elif key == "created":
                created.extend(value)
            elif key == "deleted":
                deleted.extend(value)
            else:
                traverse_diagrams(value, created, modified, deleted)
    elif isinstance(node, list):
        for item in node:
            traverse_diagrams(item, created, modified, deleted)


def transform_object_dict(original_dict):
    obj: dict = {}
    for _, object in original_dict.items():
        for category, actions in object.items():
            if category not in obj:
                obj[category] = {
                    "created": [],
                    "modified": [],
                    "deleted": [],
                }
            for action, items in actions.items():
                for item in items:
                    display_name = item["display_name"]
                    obj[category][action].append(
                        {"name": display_name, "uuid": item["uuid"]}
                    )
    return obj
