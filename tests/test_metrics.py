# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import time

from starlette import testclient

from capella_model_explorer import main

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def _idle_time_minutes(text: str) -> float:
    idletime_minutes_line = next(
        line
        for line in text.split("\n")
        if line.startswith("idletime_minutes")
    )
    return float(idletime_minutes_line.split(" ")[1])


def test_idle_time_metric():
    client = testclient.TestClient(main.app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "idletime_minutes" in response.text
    idletime_minutes_1 = _idle_time_minutes(response.text)
    time.sleep(1)
    response = client.get("/metrics")
    idletime_minutes_2 = _idle_time_minutes(response.text)
    assert idletime_minutes_2 > idletime_minutes_1
    client.close()
