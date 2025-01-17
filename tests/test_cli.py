# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import http
import itertools
import logging
import os
import subprocess
import time

import psutil
import pytest
import requests

import capella_model_explorer.constants as c

for proc in psutil.process_iter(["name", "environ"]):
    assert proc.info["name"] != "uvicorn", (
        "Run this test module without any uvicorn processes running."
    )

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def wait_for_server_startup(process, timeout=10):
    startup_message = "Application startup complete."
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(
                "Server did not start within the timeout period."
            )
        output = process.stdout.readline().decode("utf-8")
        print(output, end="")
        if startup_message in output:
            break


env_var_options = {
    "CME_HOST": [None, "localhost", "127.0.0.1"],
    "CME_PORT": [None, "7031"],
    "CME_MODEL": [
        None,
        "git+https://github.com/DSD-DBS/Capella-IFE-sample.git",
    ],
    "CME_ROUTE_PREFIX": [None, "/test-prefix"],
    "CME_TEMPLATES_DIR": [None, "tests/data/templates"],
}

# Generate all possible permutations of the environment variables
env_var_permutations = [
    dict(zip(env_var_options.keys(), values, strict=True))
    for values in itertools.product(*env_var_options.values())
]
# Create a list of identifiers for each permutation
env_var_ids = [
    ", ".join(f"{key}={value}" for key, value in env_vars.items())
    for env_vars in env_var_permutations
]


@pytest.mark.xdist_group(name="run_local")
@pytest.mark.parametrize("env_vars", env_var_permutations, ids=env_var_ids)
@pytest.mark.skipif(
    os.getenv("SKIP_LONG_RUNNING_TESTS", "false").lower() in ("true", "1"),
    reason="Skipping long running tests",
)
class TestRunSubcommand:
    def test_run_local(self, env_vars, monkeypatch):
        # Set or unset environment variables based on the test case
        for var, value in env_vars.items():
            if value is None:
                monkeypatch.delenv(var, raising=False)
            else:
                monkeypatch.setenv(var, value)
        for proc in psutil.process_iter(["name", "environ"]):
            assert proc.info["name"] != "uvicorn", (
                "Run pytest without any uvicorn processes running."
            )
        cmd = ["cme", "run", "local"]
        os.environ["CME_LIVE_MODE"] = "0"
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as process:
            wait_for_server_startup(process)
            host = os.getenv("CME_HOST", c.HOST)
            port = os.getenv("CME_PORT", c.PORT)
            base_url = f"http://{host}:{port}"
            prefix = os.getenv("CME_ROUTE_PREFIX", c.ROUTE_PREFIX)
            home_url = f"{base_url}{prefix}"
            logger.info("Checking %s", home_url)
            response = requests.get(home_url, timeout=0.5)
            assert response.status_code == http.HTTPStatus.OK
            response = requests.post(f"{base_url}/shutdown", timeout=0.5)
            assert response.status_code == http.HTTPStatus.ACCEPTED
