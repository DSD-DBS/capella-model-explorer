# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import pathlib
import shlex
import subprocess
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
    if not list(pathlib.Path().glob("static/css/main-*.css")):
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
    cmd.append("capella_model_explorer.main:app")
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
    time.sleep(1)  # avoid direct uvicorn reload when css file is written
    if not pathlib.Path(c.TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory not found: {c.TEMPLATES_DIR}")
    subprocess.check_output(["uvicorn", "--version"])
    print("Running the application locally...")
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
        "capella_model_explorer.main:app",
    ]
    print(" ".join(uvicorn_cmd))
    tailwind_proc = build_css(watch=True)
    uvicorn_proc = subprocess.Popen(
        uvicorn_cmd,
        env=os.environ
        | {
            "CME_LIVE_MODE": "1",
            "CME_MODEL": c.MODEL,
            "CME_TEMPLATES_DIR": c.TEMPLATES_DIR,
        },
    )
    if tailwind_proc is not None:
        try:
            with tailwind_proc, uvicorn_proc:
                while True:
                    time.sleep(3600)
        except KeyboardInterrupt:
            tailwind_proc.terminate()
            uvicorn_proc.terminate()


def build_css(watch) -> subprocess.Popen | None:
    """Build style sheet using Tailwind CSS."""
    for file in pathlib.Path().glob("static/css/main-*.css"):
        file.unlink()
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
        f"static/css/main-{capella_model_explorer.__version__}.min.css",
    ]
    if watch:
        tailwind_cmd.append("--watch")
        print(" ".join(tailwind_cmd))
        return subprocess.Popen(tailwind_cmd)
    subprocess.check_call(tailwind_cmd)
    return None


def build_image():
    if pathlib.Path.cwd().name != "capella-model-explorer":
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
    run_parser = subparsers.add_parser("run", help="Run the application")
    run_subparsers = run_parser.add_subparsers(
        dest="subcommand", required=True, help="Subcommands for run"
    )

    templ_reload_hlp = " The app reloads when templates are modified."
    opt_env_vars_hlp = " This command accepts optional environment variables."
    host_hlp = (
        " CME_HOST sets the host to bind the app to"
        f" (default: {c.Defaults.host})"
    )
    live_hlp = (
        " CME_LIVE_MODE controls (0: off, 1: on) template live reloading"
        f" (default: {'1' if c.Defaults.live_mode else '0'})"
    )
    model_hlp = f" CME_MODEL specifes the model (default: {c.Defaults.model})"
    port_hlp = (
        f" CME_PORT sets the port the app listens to"
        f" (default: {c.Defaults.port})"
    )
    route_prefix_hlp = (
        f" CME_ROUTE_PREFIX sets a route prefix (e.g. '/cme') to use"
        " (default: "
        f"{c.Defaults.route_prefix if c.Defaults.route_prefix else "''"})"
    )
    templates_dir_hlp = (
        f" CME_TEMPLATES_DIR sets the directory containing the templates"
        f" (default: {c.Defaults.templates_dir.resolve()})"
    )
    run_subparsers.add_parser(
        "container",
        help=(f"Run the application in a container. {templ_reload_hlp}"),
        description=(
            " Run the application in a container."
            + templ_reload_hlp
            + opt_env_vars_hlp
            + " CME_DOCKER_IMAGE_NAME"
            f" (default: {c.Defaults.docker_image_name})"
            f",{model_hlp}"
            f",{templates_dir_hlp}"
            f",{route_prefix_hlp}"
            f",{live_hlp}"
            f",{port_hlp}"
        ),
    )
    run_subparsers.add_parser(
        "local",
        help=(f"Run the application locally. {templ_reload_hlp}"),
        description=(
            "Run the application locally."
            + templ_reload_hlp
            + opt_env_vars_hlp
            + live_hlp
            + f",{host_hlp}"
            f",{model_hlp}"
            f",{port_hlp}"
            f",{route_prefix_hlp}"
            f",{templates_dir_hlp}"
        ),
    )
    run_subparsers.add_parser(
        "local-dev",
        help=(
            "Run the application locally in development mode with full reload."
        ),
        description=(
            "Run the application locally in development mode with full reload."
            " The app reloads when templates, CSS, JS, Python files change."
            + opt_env_vars_hlp
            + live_hlp
            + f",{host_hlp}"
            f",{model_hlp}"
            f",{port_hlp}"
            f",{route_prefix_hlp}"
            f",{templates_dir_hlp}"
        ),
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="Run build process")
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
        if args.subcommand == "container":
            run_container()
        elif args.subcommand == "local":
            run_local()
        elif args.subcommand == "local-dev":
            run_local_dev()
    elif args.command == "build":
        if args.subcommand == "css":
            build_css(watch=False)
        elif args.subcommand == "image":
            build_image()
    elif args.command == "pre-commit-setup":
        pre_commit_setup()


if __name__ == "__main__":
    main()
