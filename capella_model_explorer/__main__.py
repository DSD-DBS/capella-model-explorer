# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import pathlib
import subprocess
import threading
import time
import typing as t

import capella_model_explorer
import capella_model_explorer.constants as c

DEFAULTS: t.Final[dict[str, str]] = {
    "DOCKER_IMAGE_NAME": "capella-model-explorer:latest",
    "LIVE_MODE": c.LIVE_MODE_DEFAULT,
    "ROUTE_PREFIX": c.ROUTE_PREFIX_DEFAULT,
    "HOST": "0.0.0.0",
    "PORT": "8000",
    "MODEL": "git+https://github.com/DSD-DBS/Capella-IFE-sample.git",
    "TEMPLATES_DIR": "templates",
    "TAILWIND_CSS_CLI_VERSION": "4.0.0",
    "TAILWIND_CSS_VERSION": "4.0.0",
    "TAILWIND_CSS_TYPOGRAPHY_VERSION": "0.5.16",
}

# configuration
TAILWIND_CSS_CLI_VERSION: t.Final[str] = os.getenv(
    "CME_TAILWIND_CSS_CLI_VERSION", DEFAULTS["TAILWIND_CSS_CLI_VERSION"]
)
TAILWIND_CSS_TYPOGRAPHY_VERSION: t.Final[str] = os.getenv(
    "CME_TAILWIND_CSS_TYPOGRAPHY_VERSION",
    DEFAULTS["TAILWIND_CSS_TYPOGRAPHY_VERSION"],
)
TAILWIND_CSS_VERSION: t.Final[str] = os.getenv(
    "CME_TAILWIND_CSS_VERSION", DEFAULTS["TAILWIND_CSS_VERSION"]
)
HOST: t.Final[str] = os.getenv("CME_HOST", DEFAULTS["HOST"])
PORT: t.Final[str] = os.getenv("CME_PORT", DEFAULTS["PORT"])
MODEL: t.Final[str] = os.getenv("CME_MODEL", DEFAULTS["MODEL"])
TEMPLATES_DIR: t.Final[str] = os.getenv(
    "CME_TEMPLATES_DIR", DEFAULTS["TEMPLATES_DIR"]
)


def _check_cmd_run(cmd: list[str], errmsg: str = "") -> None:
    """Check if a command is available."""
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print(f"Command '{cmd[0]}' not found. {errmsg}")
        raise SystemExit(1) from None


def _install_npm_pkgs(pkgs: list[str]) -> None:
    _check_cmd_run(["npm", "--version"], "Install Node package manager npm.")
    for pkg in pkgs:
        pkg_ = pkg
        if pkg_.count("@") == 1 and pkg_[0] == "@":
            pkg_name = pkg_
        elif pkg_.count("@") == 1 and pkg_[0] != "@":
            pkg_name = pkg_.split("@")[0]
        elif pkg_.count("@") > 1:
            while pkg_[-1].isdigit() or pkg_[-1] == "." or pkg_[-1] == "@":
                pkg_ = pkg_[:-1]
            pkg_name = pkg_
        pkg_path = pathlib.Path("node_modules") / pkg_name
        if not pkg_path.is_dir():
            cmd = ["npm", "install", "-D", pkg]
            print(" ".join(cmd))
            subprocess.run(
                cmd,
                check=True,
                capture_output=False,
            )


def run_container():
    _check_cmd_run(["docker", "--version"], "Install Docker.")
    cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        "capella-model-explorer",
        "-e",
        f"CME_LIVE_MODE={'1' if c.LIVE_MODE else '0'}",
        "-e",
        f"CME_MODEL={MODEL}",
        "-e",
        f"CME_PORT={PORT}",
        "-e",
        f"CME_ROUTE_PREFIX={c.ROUTE_PREFIX}",
        "-p",
        f"{PORT}:{PORT}",
    ]
    if TEMPLATES_DIR:
        if pathlib.Path(TEMPLATES_DIR).is_dir():
            cmd.extend(
                [
                    "-v",
                    f"{pathlib.Path(TEMPLATES_DIR).resolve()}:/app/templates",
                ]
            )
        else:
            raise SystemExit(
                f"Templates directory '{TEMPLATES_DIR}' not found."
            )
    cmd.append(
        os.getenv(
            "CME_DOCKER_IMAGE_NAME",
            DEFAULTS["DOCKER_IMAGE_NAME"],
        )
    )
    print(" ".join(cmd))
    subprocess.run(
        cmd,
        check=True,
        capture_output=False,
    )


def run_local():
    """Run the application locally."""
    if not pathlib.Path(TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory '{TEMPLATES_DIR}' not found.")
    _check_cmd_run(["uvicorn", "--version"], "Install Uvicorn.")
    print("Running the application locally...")
    cmd = [
        "uvicorn",
        "--host",
        HOST,
        "--port",
        PORT,
    ]
    if c.LIVE_MODE:
        cmd.extend(
            [
                "--reload",
                "--reload-exclude",
                "git_askpass.py",
                "--reload-dir",
                TEMPLATES_DIR,
                "--reload-include",
                "*.j2",
            ]
        )
    cmd.append("capella_model_explorer.main:app")
    print(" ".join(cmd))
    subprocess.run(
        cmd,
        env=os.environ
        | {
            "CME_LIVE_MODE": "1" if c.LIVE_MODE else "0",
            "CME_MODEL": MODEL,
            "CME_ROUTE_PREFIX": c.ROUTE_PREFIX,
            "CME_TAILWIND_CSS_VERSION": DEFAULTS["TAILWIND_CSS_VERSION"],
            "CME_TAILWIND_CSS_TYPOGRAPHY_VERSION": (
                DEFAULTS["TAILWIND_CSS_TYPOGRAPHY_VERSION"]
            ),
            "CME_TEMPLATES_DIR": TEMPLATES_DIR,
        },
        check=True,
        capture_output=False,
    )


def run_local_dev():
    print("Running the application locally with full reload...")
    thread = threading.Thread(target=build_css, kwargs={"watch": True})
    thread.start()
    time.sleep(1)  # avoid direct uvicorn reload when css file is written
    if not pathlib.Path(TEMPLATES_DIR).is_dir():
        raise SystemExit(f"Templates directory '{TEMPLATES_DIR}' not found.")
    _check_cmd_run(["uvicorn", "--version"], "Install Uvicorn.")
    print("Running the application locally...")
    cmd = [
        "uvicorn",
        "--host",
        HOST,
        "--port",
        PORT,
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
    print(" ".join(cmd))
    subprocess.run(
        cmd,
        env=os.environ
        | {
            "CME_LIVE_MODE": "1",
            "CME_MODEL": MODEL,
            "CME_TEMPLATES_DIR": TEMPLATES_DIR,
            "CME_TAILWIND_CSS_VERSION": DEFAULTS["TAILWIND_CSS_VERSION"],
            "CME_TAILWIND_CSS_TYPOGRAPHY_VERSION": (
                DEFAULTS["TAILWIND_CSS_TYPOGRAPHY_VERSION"]
            ),
        },
        check=True,
        capture_output=False,
    )


def build_css(watch):
    """Build style sheet using Tailwind CSS."""
    for file in pathlib.Path().glob("static/css/main-*.css"):
        file.unlink()
    _install_npm_pkgs(
        [
            f"tailwindcss@{DEFAULTS['TAILWIND_CSS_VERSION']}",
            f"@tailwindcss/cli@{DEFAULTS['TAILWIND_CSS_CLI_VERSION']}",
            f"@tailwindcss/typography@{DEFAULTS['TAILWIND_CSS_TYPOGRAPHY_VERSION']}",
        ]
    )
    exe = "node_modules/.bin/tailwindcss"
    _check_cmd_run([exe, "--help"], "Install Tailwind CSS CLI.")
    print("Building style sheet...")
    input_css = pathlib.Path("static/css/input.css")
    if not input_css.is_file():
        raise SystemExit(f"Input CSS file '{input_css}' not found.")
    cmd = [
        exe,
        "--minify",
        "--input",
        str(input_css),
        "--output",
        f"static/css/main-{capella_model_explorer.__version__}.min.css",
    ]
    if watch:
        cmd.append("--watch")
    print(" ".join(cmd))
    subprocess.run(
        cmd,
        check=True,
        capture_output=False,
    )


def build_image():
    _check_cmd_run(["docker", "--version"], "Install Docker.")
    cmd = [
        "docker",
        "build",
        "--no-cache",
        "--build-arg",
        f"TAILWIND_CSS_VERSION={DEFAULTS['TAILWIND_CSS_VERSION']}",
        "--build-arg",
        f"TAILWIND_CSS_CLI_VERSION={DEFAULTS['TAILWIND_CSS_CLI_VERSION']}",
        "--build-arg",
        "TAILWIND_CSS_TYPOGRAPHY_VERSION"
        f"={DEFAULTS['TAILWIND_CSS_TYPOGRAPHY_VERSION']}",
        "-t",
        f"capella-model-explorer:{capella_model_explorer.__version__}",
        ".",
    ]
    print(" ".join(cmd))
    subprocess.run(
        cmd,
        check=True,
        capture_output=False,
    )


def pre_commit_setup():
    print("Installing tools needed for pre-commit hooks...")
    _install_npm_pkgs(
        [
            "prettier@3.4.2",
            "prettier-plugin-jinja-template@2.0.0",
            "remark-parse@11.0.0",
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "CLI for managing the application. Every command"
            " has its own `--help` option."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the application")
    run_subparsers = run_parser.add_subparsers(
        dest="subcommand", required=True, help="Subcommands for run"
    )

    if DEFAULTS["ROUTE_PREFIX"]:
        cme_route_prefix_default = DEFAULTS["ROUTE_PREFIX"]
    else:
        cme_route_prefix_default = "''"

    templ_reload_hlp = " The app reloads when templates are modified."
    opt_env_vars_hlp = " This command accepts optional environment variables."
    host_hlp = (
        " CME_HOST sets the host to bind the app to"
        f" (default: {DEFAULTS['HOST']})"
    )
    live_hlp = (
        " CME_LIVE_MODE controls (0: off, 1: on) template live reloading"
        f" (default: {DEFAULTS['LIVE_MODE']})"
    )
    model_hlp = f" CME_MODEL specifes the model (default: {DEFAULTS['MODEL']})"
    port_hlp = (
        f" CME_PORT sets the port the app listens to"
        f" (default: {DEFAULTS['PORT']})"
    )
    route_prefix_hlp = (
        f" CME_ROUTE_PREFIX sets a route prefix (e.g. '/cme') to use"
        f" (default: {cme_route_prefix_default})"
    )
    templates_dir_hlp = (
        f" CME_TEMPLATES_DIR sets the directory containing the templates"
        f" (default: {DEFAULTS['TEMPLATES_DIR']})"
    )
    run_subparsers.add_parser(
        "container",
        help=(f"Run the application in a container. {templ_reload_hlp}"),
        description=(
            " Run the application in a container."
            + templ_reload_hlp
            + opt_env_vars_hlp
            + " CME_DOCKER_IMAGE_NAME"
            f" (default: {DEFAULTS['DOCKER_IMAGE_NAME']})"
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
