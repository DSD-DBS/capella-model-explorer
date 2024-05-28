# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import pathlib
import subprocess


def run_git_command(cmd: list[str]):
    try:
        return subprocess.run(
            ["git", *cmd],
            check=True,
            capture_output=True,
            cwd=pathlib.Path(__file__).parent,
        ).stdout.decode()
    except subprocess.CalledProcessError:
        return "No tags found"


if os.getenv("MODE") == "production":
    path = pathlib.Path(__file__).parent / "dist" / "static" / "version.json"
else:
    path = pathlib.Path(__file__).parent / "public" / "static" / "version.json"

path.write_text(
    json.dumps(
        {
            "git": {
                "version": run_git_command(["describe", "--tags"]).strip(),
                "tag": run_git_command(
                    ["describe", "--tags", "--abbrev=0"]
                ).strip(),
            }
        }
    )
)
