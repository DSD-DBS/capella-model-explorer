# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""CLI for the Capella Model Explorer application."""

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

import capella_model_explorer
import capella_model_explorer.constants as c

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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

    assert (tailwind_proc := build_css(watch=True))
    time.sleep(1)
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


def build_image() -> None:
    if not (pathlib.Path.cwd() / "capella_model_explorer").is_dir():
        raise SystemExit("Run this command from the root of the project.")

    docker = _find_exe("docker")
    cmd = [
        docker,
        "build",
        "--no-cache",
        "-t",
        f"capella-model-explorer:{capella_model_explorer.__version__}",
        ".",
    ]
    logger.info(shlex.join(cmd))
    subprocess.check_call(cmd)


def pre_commit_setup() -> None:
    pre_commit = _find_exe("pre-commit")
    logger.info("Installing tools needed for pre-commit hooks...")
    _install_npm_pkgs()
    logger.info("Installing pre-commit hooks...")
    subprocess.check_call([pre_commit, "install-hooks"])
    subprocess.check_call([pre_commit, "install"])


def _find_exe(name: str) -> str:
    if not (path := shutil.which(name)):
        raise SystemExit(f"Cannot find {name!r}, install it and try again")
    return path


@click.group()
def main() -> None:
    """CLI for managing the Capella Model Explorer application."""


@main.command()
@click.option(
    "--container",
    is_flag=True,
    help="Launch as a Docker container.",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Launch in development mode with full auto-reload.",
)
@click.option(
    "--host",
    envvar="CME_HOST",
    default=c.Defaults.host,
    help=f"The hostname or IP address to bind to. Default: {c.Defaults.host}. "
    "Ignored when running with '--container'.",
)
@click.option(
    "--port",
    envvar="CME_PORT",
    default=c.Defaults.port,
    help=f"The port to listen on. Default: {c.Defaults.port}.",
)
@click.option(
    "--model",
    envvar="CME_MODEL",
    default=c.Defaults.model,
    help="The Capella model to load (file, URL or JSON string). "
    f"Default: {c.Defaults.model}.",
)
@click.option(
    "--templates-dir",
    envvar="CME_TEMPLATES_DIR",
    default=str(c.Defaults.templates_dir.resolve()),
    help="The directory containing the templates. "
    f"Default: {c.Defaults.templates_dir.resolve()}.",
)
@click.option(
    "--live-mode",
    envvar="CME_LIVE_MODE",
    default="1" if c.Defaults.live_mode else "0",
    type=click.Choice(["0", "1"]),
    help="Control automatic reloading of templates on changes. "
    "Set to 1 to enable, 0 to disable. "
    f"Default: {'1' if c.Defaults.live_mode else '0'}. "
    "Ignored in '--dev' mode.",
)
@click.option(
    "--route-prefix",
    envvar="CME_ROUTE_PREFIX",
    default="",
    help="Add a prefix to all web routes. "
    "(Note: this prefix does not apply to '/metrics').",
)
@click.option(
    "--docker-image-name",
    envvar="CME_DOCKER_IMAGE_NAME",
    default=c.Defaults.docker_image_name,
    help="The Docker image to use with '--container'. "
    f"Default: {c.Defaults.docker_image_name}.",
)
def run(
    container: bool,  # noqa: FBT001
    dev: bool,  # noqa: FBT001
    host: str,
    port: int,
    model: str,
    templates_dir: str,
    live_mode: str,
    route_prefix: str,
    docker_image_name: str,
) -> None:
    """Run the application."""
    os.environ["CME_HOST"] = host
    os.environ["CME_PORT"] = str(port)
    os.environ["CME_MODEL"] = model
    os.environ["CME_TEMPLATES_DIR"] = templates_dir
    os.environ["CME_LIVE_MODE"] = live_mode
    os.environ["CME_ROUTE_PREFIX"] = route_prefix
    os.environ["CME_DOCKER_IMAGE_NAME"] = docker_image_name
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
    "--css",
    "css_flag",
    is_flag=True,
    help="Build the style sheet with Tailwind CSS.",
)
@click.option(
    "--container-image",
    "container_image",
    is_flag=True,
    help="Build the Docker container image.",
)
def build(css_flag: bool, container_image: bool) -> None:  # noqa: FBT001
    """Run a specified build process."""
    if css_flag and container_image:
        raise click.UsageError(
            "Options --css and --container-image are mutually exclusive."
        )

    if not (css_flag or container_image):
        raise click.UsageError(
            "Please specify one of --css or --container-image."
        )

    if css_flag:
        build_css(watch=False)
    if container_image:
        build_image()


@main.command("pre-commit-setup")
def pre_commit_setup_cmd() -> None:
    """Install tools needed for pre-commit hooks."""
    pre_commit_setup()


if __name__ == "__main__":
    main()
