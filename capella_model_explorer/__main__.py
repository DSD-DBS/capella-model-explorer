# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Command line interface for the application."""

from __future__ import annotations

import importlib
import json
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import time
import typing as t

import click
import uvicorn

import capella_model_explorer.constants as c
from capella_model_explorer import app

logger = logging.getLogger(__name__)


def _install_npm_pkgs() -> None:
    npm = _find_exe("npm")
    cmd = [npm, "clean-install"]
    logger.info(shlex.join(cmd))
    subprocess.check_call(cmd)


def run_container(*, log_config: dict[str, t.Any]) -> None:
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
        f"-eCME_LOG_CONFIG={json.dumps(log_config)}",
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


def run_local(*, rebuild: bool, log_config: dict[str, t.Any]) -> None:
    """Run the application locally."""
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")

    if rebuild or not pathlib.Path(c.main_css_path).exists():
        build_css(watch=False)

    logger.info("Running the application locally...")
    uvicorn.run(
        app="capella_model_explorer.app:app",
        host=c.HOST,
        port=c.PORT,
        log_config=log_config,
        reload=c.LIVE_MODE,
        reload_dirs=str(c.TEMPLATES_DIR) if c.LIVE_MODE else None,
        reload_excludes="git_askpass.py" if c.LIVE_MODE else None,
        reload_includes="*.j2" if c.LIVE_MODE else None,
    )


def run_local_dev(*, log_config: dict[str, t.Any]) -> None:
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
                log_config=log_config,
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
    logger.info("Building style sheet...")

    _install_npm_pkgs()
    exe = shutil.which("node_modules/.bin/tailwindcss")
    if exe is None:
        raise SystemExit("tailwindcss failed to install, please try again")
    exe = os.path.realpath(exe)

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
@click.option(
    "--log-logfmt / --log-no-logfmt",
    envvar="CME_LOGFMT",
    default=True,
    help="Use the logfmt output format for logging",
)
@click.option(
    "--log-level",
    envvar="CME_LOG_LEVEL",
    default="INFO",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        case_sensitive=False,
    ),
)
@click.option(
    "--log-file",
    envvar="CME_LOG_FILE",
    type=click.Path(dir_okay=False),
    help="Log to this file instead of stderr",
)
@click.option(
    "--log-config",
    "raw_log_config",
    envvar="CME_LOG_CONFIG",
    default=None,
    help=(
        "A JSON-encoded log config dictionary,"
        " as understood by 'logging.config.dictConfig()'."
        " If passed, other '--log-*' arguments are ignored."
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    /,
    *,
    log_logfmt: bool,
    log_level: str,
    log_file: str | None,
    raw_log_config: str | None,
) -> None:
    """Command line interface to control the application."""
    obj = ctx.ensure_object(dict)

    if raw_log_config:
        obj["log_config"] = json.loads(raw_log_config)
    else:
        if not log_file:
            handler = {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
                "filters": ["denoise"],
            }
        else:
            handler = {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "default",
                "filters": ["denoise"],
            }

        if log_logfmt:
            formatter = {
                "()": "capella_model_explorer.core.Logfmter",
                "keys": [
                    "at",
                    "logger",
                    "msg",
                    "client_addr",
                    "method",
                    "path",
                    "http_version",
                    "status_code",
                ],
                "mapping": {
                    "at": "levelname",
                    "logger": "name",
                },
            }
        else:
            formatter = {
                "format": "%(asctime)s.%(msecs)03d <%(name)s> %(levelname)s: %(message)s",
            }

        obj["log_config"] = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": formatter},
            "filters": {
                "denoise": {
                    "()": "capella_model_explorer.core.SuppressWebsocketNoise",
                }
            },
            "handlers": {"default": handler},
            "loggers": {
                "": {"level": log_level, "handlers": ["default"]},
                "uvicorn": {"level": "NOTSET", "propagate": True},
                "uvicorn.error": {"level": "NOTSET", "propagate": True},
                "uvicorn.access": {"level": "NOTSET", "propagate": True},
            },
        }


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
    "-h",
    "--host",
    envvar="CME_HOST",
    default=c.Defaults.host,
    show_default=True,
    help="The hostname or IP address to bind to."
    " Ignored when running with '--container'.",
)
@click.option(
    "-p",
    "--port",
    envvar="CME_PORT",
    default=c.Defaults.port,
    show_default=True,
    help="The port to listen on.",
)
@click.option(
    "-m",
    "--model",
    envvar="CME_MODEL",
    default=c.Defaults.model,
    show_default=True,
    help="The Capella model to load (file, URL or JSON string).",
)
@click.option(
    "-t",
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
@click.option(
    "--skip-rebuild/--no-skip-rebuild",
    default=False,
    help="Don't rebuild already existing assets.",
)
@click.pass_context
def run(
    ctx: click.Context,
    /,
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
    skip_rebuild: bool,
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
        run_container(log_config=ctx.obj["log_config"])
    elif dev:
        run_local_dev(log_config=ctx.obj["log_config"])
    else:
        run_local(rebuild=not skip_rebuild, log_config=ctx.obj["log_config"])


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
