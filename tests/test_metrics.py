# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import time

from starlette import testclient

from capella_model_explorer import main

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def test_metrics_endpoint_available():
    client = testclient.TestClient(main.app)
    response = client.get("/metrics")
    assert response.status_code == 200
    client.close()


def _idle_time_minutes_rounded(text: str) -> str:
    idletime_minutes_line = next(
        line
        for line in text.split("\n")
        if line.startswith("idletime_minutes")
    )
    idletime_minutes = float(idletime_minutes_line.split(" ")[1])
    return f"{idletime_minutes:.2f}"


def test_idle_time_metric():
    client = testclient.TestClient(main.app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "idletime_minutes" in response.text
    idletime_minutes_rounded = _idle_time_minutes_rounded(response.text)
    assert idletime_minutes_rounded == "0.00"
    timeout = 0.6
    time.sleep(timeout)
    response = client.get("/metrics")
    actual_idletime_minutes_rounded = _idle_time_minutes_rounded(response.text)
    expected_idletime_minutes_rounded = "0.01"
    assert actual_idletime_minutes_rounded == expected_idletime_minutes_rounded
    client.close()
