# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import os
import pathlib
import shlex
import subprocess
import textwrap
import time

import capella_model_explorer
import capella_model_explorer.constants as c


def _install_npm_pkgs() -> None:
    subprocess.check_output(["npm", "--version"])
    cmd = ["npm", "clean-install"]
    print(shlex.join(cmd))
    subprocess.check_call(cmd)


def run_container():
    subprocess.check_output(["docker", "--version"])
    cmd = [
        "docker",
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
            [
                "-v",
                f"{model.resolve()}:/model",
                "-e",
                "CME_MODEL=/model",
            ]
        )
    else:
        cmd.extend(
            [
                "-e",
                f"CME_MODEL={c.MODEL}",
            ]
        )
    if pathlib.Path(c.TEMPLATES_DIR).is_dir():
        cmd.extend(
            [
                "-v",
                f"{pathlib.Path(c.TEMPLATES_DIR).resolve()}:/templates",
            ]
        )
    else:
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")
    cmd.append(c.DOCKER_IMAGE_NAME)
    print(shlex.join(cmd))
    subprocess.check_call(cmd)


def run_local():
    """Run the application locally."""
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")
    subprocess.check_output(["uvicorn", "--version"])
    if not pathlib.Path(c.main_css_path).exists():
        build_css(watch=False)
    print("Running the application locally...")
    cmd = [
        "uvicorn",
        "--host",
        c.HOST,
        "--port",
        str(c.PORT),
    ]
    if c.LIVE_MODE:
        cmd.extend(
            [
                "--reload",
                "--reload-exclude",
                "git_askpass.py",
                "--reload-dir",
                str(c.TEMPLATES_DIR),
                "--reload-include",
                "*.j2",
            ]
        )
    cmd.append("capella_model_explorer.app:app")
    print(shlex.join(cmd))
    subprocess.check_call(
        cmd,
        env=os.environ
        | {
            "CME_LIVE_MODE": "1" if c.LIVE_MODE else "0",
            "CME_MODEL": c.MODEL,
            "CME_ROUTE_PREFIX": c.ROUTE_PREFIX,
            "CME_TEMPLATES_DIR": str(c.TEMPLATES_DIR),
        },
    )


def run_local_dev() -> None:
    print("Running the application locally with full reload...")
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")
    subprocess.check_output(["uvicorn", "--version"])
    uvicorn_cmd = [
        "uvicorn",
        "--host",
        c.HOST,
        "--port",
        str(c.PORT),
        "--reload",
        "--reload-exclude",
        "git_askpass.py",
        "--reload-exclude",
        "input.css",
        "--reload-dir",
        ".",
        "--reload-include",
        "*.css",
        "--reload-include",
        "*.j2",
        "--reload-include",
        "*.js",
        "--reload-include",
        "*.py",
        "capella_model_explorer.app:app",
    ]
    print(" ".join(uvicorn_cmd))
    tailwind_proc = build_css(watch=True)
    assert tailwind_proc is not None
    time.sleep(1)  # avoid direct uvicorn reload when css file is written
    uvicorn_proc = subprocess.Popen(
        uvicorn_cmd,
        env=os.environ
        | {
            "CME_LIVE_MODE": "1",
            "CME_MODEL": c.MODEL,
            "CME_TEMPLATES_DIR": c.TEMPLATES_DIR,
        },
    )
    try:
        with tailwind_proc, uvicorn_proc:
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        tailwind_proc.terminate()
        uvicorn_proc.terminate()


def build_css(*, watch: bool) -> subprocess.Popen | None:
    """Build style sheet using Tailwind CSS."""
    _install_npm_pkgs()
    exe = "node_modules/.bin/tailwindcss"
    subprocess.check_output([exe, "--help"])
    print("Building style sheet...")
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
        print(shlex.join(tailwind_cmd))
        return subprocess.Popen(tailwind_cmd)
    print(shlex.join(tailwind_cmd))
    subprocess.check_call(tailwind_cmd)
    return None


def build_image():
    if not (pathlib.Path.cwd() / "capella_model_explorer").is_dir():
        raise SystemExit("Run this command from the root of the project.")
    subprocess.check_output(["docker", "--version"])
    cmd = [
        "docker",
        "build",
        "--no-cache",
        "-t",
        f"capella-model-explorer:{capella_model_explorer.__version__}",
        ".",
    ]
    print(shlex.join(cmd))
    subprocess.check_call(cmd)


def pre_commit_setup():
    print("Installing tools needed for pre-commit hooks...")
    _install_npm_pkgs()
    print("Installing pre-commit hooks...")
    subprocess.check_call(["pre-commit", "install-hooks"])
    subprocess.check_call(["pre-commit", "install"])


def main():
    parser = argparse.ArgumentParser(
        description=(
            "CLI for managing the application. Every command"
            " has its own `--help` option."
        )
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {capella_model_explorer.__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Run command
    run_description = textwrap.dedent(
        f"""\
        Run the application.

        The following environment variables are honored:

        CME_HOST: The hostname or IP address to bind to. Default: {c.Defaults.host}
            Ignored when running with '--container'.
        CME_PORT: The port to listen on. Default: {c.Defaults.port}
        CME_MODEL: The Capella model to load, either as file, URL or JSON string.
            For details, refer to the capellambse documentation:
            https://dsd-dbs.github.io/py-capellambse/start/specifying-models.html
            Default: {c.Defaults.model}
        CME_TEMPLATES_DIR: The directory containing the templates.
            Default: {c.Defaults.templates_dir.resolve()}
        CME_LIVE_MODE: Control automatic reloading of templates on changes.
            Set to 1 to enable, 0 to disable. Default: {"01"[c.Defaults.live_mode]}
            Ignored in '--dev' mode, where auto-reloading for
            both templates and code is always enabled.
        CME_ROUTE_PREFIX: Add a prefix to all web routes.
            Note that this prefix does not apply to '/metrics'.
        CME_DOCKER_IMAGE_NAME: The Docker image to use with '--container'.
            Default: {c.Defaults.docker_image_name}
        """
    )
    run_parser = subparsers.add_parser(
        "run",
        description=run_description,
        help="Run the application with various options.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    run_mode_group = run_parser.add_mutually_exclusive_group()
    run_mode_group.add_argument(
        "--dev",
        action="store_true",
        help="Launch in development mode with full auto-reload.",
    )
    run_mode_group.add_argument(
        "--container",
        action="store_true",
        help=(
            "Launch as a Docker container. See also: cme build image --help"
        ),
    )

    # Build command
    build_parser = subparsers.add_parser(
        "build", help="Run a specified build process"
    )
    build_subparsers = build_parser.add_subparsers(
        dest="subcommand", required=True, help="Subcommands for build"
    )

    build_subparsers.add_parser(
        "css",
        help="Build style sheet with Tailwind CSS CLI.",
    )
    build_subparsers.add_parser("image", help="Build Docker image.")

    # Pre-commit setup command
    subparsers.add_parser(
        "pre-commit-setup", help="Install tools needed for pre-commit hooks"
    )

    args = parser.parse_args()

    if args.command == "run":
        if args.container:
            run_container()
        elif args.dev:
            run_local_dev()
        else:
            run_local()
    elif args.command == "build":
        if args.subcommand == "css":
            build_css(watch=False)
        elif args.subcommand == "image":
            build_image()
    elif args.command == "pre-commit-setup":
        pre_commit_setup()


if __name__ == "__main__":
    main()
