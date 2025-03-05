# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Command line interface for the application."""

from __future__ import annotations

import importlib
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import time

import click
import uvicorn

import capella_model_explorer.constants as c
from capella_model_explorer import app, core

logger = logging.getLogger(__name__)
core.setup_logging(logger)


def _install_npm_pkgs() -> None:
    npm = _find_exe("npm")
    cmd = [npm, "clean-install"]
    logger.info(shlex.join(cmd))
    subprocess.check_call(cmd)


def run_container() -> None:
    docker = _find_exe("docker")
    cmd = [
        docker,
        "run",
        "--rm",
        "-it",
        "--name",
        "cme",
        "-e",
        f"CME_LIVE_MODE={'1' if c.LIVE_MODE else '0'}",
        "-e",
        f"CME_PORT={c.PORT}",
        "-e",
        f"CME_ROUTE_PREFIX={c.ROUTE_PREFIX}",
        "-p",
        f"{c.PORT}:{c.PORT}",
    ]
    model = pathlib.Path(c.MODEL)
    if model.is_file() and str(model).lower().endswith(".aird"):
        model = model.parent
    if model.is_dir():
        cmd.extend(
            ["-v", f"{model.resolve()}:/model", "-e", "CME_MODEL=/model"]
        )
    else:
        cmd.extend(["-e", f"CME_MODEL={c.MODEL}"])
    if pathlib.Path(c.TEMPLATES_DIR).is_dir():
        cmd.extend(
            ["-v", f"{pathlib.Path(c.TEMPLATES_DIR).resolve()}:/templates"]
        )
    else:
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")

    cmd.append(c.DOCKER_IMAGE_NAME)
    logger.info(shlex.join(cmd))
    subprocess.check_call(cmd)


def run_local() -> None:
    """Run the application locally."""
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")

    if not pathlib.Path(c.main_css_path).exists():
        build_css(watch=False)

    logger.info("Running the application locally...")
    uvicorn.run(
        app="capella_model_explorer.app:app",
        host=c.HOST,
        port=c.PORT,
        reload=c.LIVE_MODE,
        reload_dirs=str(c.TEMPLATES_DIR),
        reload_excludes="git_askpass.py",
        reload_includes="*.j2",
    )


def run_local_dev() -> None:
    logger.info("Running the application locally with full reload...")
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")

    tailwind_proc = build_css(watch=True)
    assert tailwind_proc is not None
    time.sleep(1)  # avoid direct uvicorn reload when css file is written

    try:
        with tailwind_proc:
            uvicorn.run(
                app="capella_model_explorer.app:app",
                host=c.HOST,
                port=c.PORT,
                reload=True,
                reload_dirs=".",
                reload_excludes=[
                    "git_askpass.py",
                    "input.css",
                ],
                reload_includes=[
                    "*.css",
                    "*.j2",
                    "*.js",
                    "*.py",
                ],
            )
    except KeyboardInterrupt:
        tailwind_proc.terminate()


def build_css(*, watch: bool) -> subprocess.Popen | None:
    """Build style sheet using Tailwind CSS."""
    _install_npm_pkgs()
    exe = shutil.which("node_modules/.bin/tailwindcss")
    if exe is None:
        raise SystemExit("tailwindcss failed to install, please try again")
    exe = os.path.realpath(exe)

    logger.info("Building style sheet...")
    input_css = pathlib.Path("static/css/input.css")
    if not input_css.is_file():
        raise SystemExit(f"Input CSS file not found: {input_css}")

    tailwind_cmd = [
        exe,
        "--minify",
        "--input",
        str(input_css),
        "--output",
        c.main_css_path,
    ]
    if watch:
        tailwind_cmd.append("--watch")
        logger.info(shlex.join(tailwind_cmd))
        return subprocess.Popen(tailwind_cmd)

    logger.info(shlex.join(tailwind_cmd))
    subprocess.check_call(tailwind_cmd)
    return None


def _find_exe(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise SystemExit(f"Cannot find {name!r}, install it and try again")
    return path


@click.group()
def main() -> None:
    """Command line interface to control the application."""


@main.command()
@click.option(
    "--container",
    is_flag=True,
    default=False,
    show_default=True,
    help="Launch as a Docker container.",
)
@click.option(
    "--dev",
    is_flag=True,
    show_default=True,
    help="Launch in development mode with full auto-reload."
    " This option cannot be used together with --container.",
)
@click.option(
    "--host",
    envvar="CME_HOST",
    default=c.Defaults.host,
    show_default=True,
    help="The hostname or IP address to bind to."
    " Ignored when running with '--container'.",
)
@click.option(
    "--port",
    envvar="CME_PORT",
    default=c.Defaults.port,
    show_default=True,
    help="The port to listen on.",
)
@click.option(
    "--model",
    envvar="CME_MODEL",
    default=c.Defaults.model,
    show_default=True,
    help="The Capella model to load (file, URL or JSON string).",
)
@click.option(
    "--templates-dir",
    envvar="CME_TEMPLATES_DIR",
    default=str(c.Defaults.templates_dir.resolve()),
    show_default=True,
    help="The directory containing the templates.",
)
@click.option(
    "--live-mode/--no-live-mode",
    envvar="CME_LIVE_MODE",
    default=c.Defaults.live_mode,
    show_default=True,
    help=(
        "Control automatic reloading of templates on changes."
        " Ignored in '--dev' mode, where it is always enabled."
    ),
)
@click.option(
    "--route-prefix",
    envvar="CME_ROUTE_PREFIX",
    default="",
    show_default=True,
    help="Add a prefix to all web routes."
    f" (Note: this prefix does not apply to '{app.metrics.to()}').",
)
@click.option(
    "--image",
    envvar="CME_DOCKER_IMAGE_NAME",
    default=c.Defaults.docker_image_name,
    show_default=True,
    help="The Docker image to use with '--container'.",
)
def run(
    *,
    container: bool,
    dev: bool,
    host: str,
    port: int,
    model: str,
    templates_dir: str,
    live_mode: bool,
    route_prefix: str,
    image: str,
) -> None:
    """Run the application."""
    os.environ["CME_HOST"] = host
    os.environ["CME_PORT"] = str(port)
    os.environ["CME_MODEL"] = model
    os.environ["CME_TEMPLATES_DIR"] = templates_dir
    os.environ["CME_LIVE_MODE"] = "1" if live_mode else "0"
    os.environ["CME_ROUTE_PREFIX"] = route_prefix
    os.environ["CME_DOCKER_IMAGE_NAME"] = image
    importlib.reload(c)

    if container and dev:
        raise click.UsageError(
            "Options --container and --dev are mutually exclusive."
        )
    if container:
        run_container()
    elif dev:
        run_local_dev()
    else:
        run_local()


@main.command()
@click.option(
    "--watch",
    is_flag=True,
    default=False,
    show_default=True,
    help="Watch for changes and rebuild automatically.",
)
def build(*, watch: bool) -> None:
    """Build style sheet using Tailwind CSS."""
    build_css(watch=watch)


@main.command("pre-commit-setup")
def pre_commit_setup_cmd() -> None:
    """Install tools needed for pre-commit hooks."""
    pre_commit = _find_exe("pre-commit")
    logger.info("Installing tools needed for pre-commit hooks...")
    _install_npm_pkgs()
    logger.info("Installing pre-commit hooks...")
    subprocess.check_call([pre_commit, "install-hooks"])
    subprocess.check_call([pre_commit, "install"])


if __name__ == "__main__":
    main()
