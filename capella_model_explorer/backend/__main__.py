# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

import capellambse
import click
import uvicorn

from . import explorer

HOST = os.getenv("CAPELLA_MODEL_EXPLORER_HOST_IP", "0.0.0.0")
PORT = os.getenv("CAPELLA_MODEL_EXPLORER_PORT", "8000")


@click.command()
@click.argument("model", type=capellambse.ModelCLI())
@click.argument("templates", type=click.Path(exists=True))
def run(model: capellambse.MelodyModel, templates: Path | str):
    backend = explorer.CapellaModelExplorerBackend(Path(templates), model)
    uvicorn.run(backend.app, host=HOST, port=int(PORT))


if __name__ == "__main__":
    run()
