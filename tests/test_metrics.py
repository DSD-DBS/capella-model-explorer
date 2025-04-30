# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import time

from starlette import testclient

from capella_model_explorer import app


def _idle_time_minutes(text: str) -> float:
    idle_time_minutes_line = next(
        line
        for line in text.split("\n")
        if line.startswith("idletime_minutes")
    )
    return float(idle_time_minutes_line.split(" ")[1])


def test_idle_time_metric():
    client = testclient.TestClient(app.app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "idletime_minutes" in response.text
    idle_time_minutes_1 = _idle_time_minutes(response.text)
    time.sleep(1)
    response = client.get("/metrics")
    idle_time_minutes_2 = _idle_time_minutes(response.text)
    assert idle_time_minutes_2 > idle_time_minutes_1
    client.close()
