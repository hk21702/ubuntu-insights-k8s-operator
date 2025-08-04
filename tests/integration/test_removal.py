#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import jubilant
import pytest
import requests


def test_active(juju: jubilant.Juju, app: str):
    """Check that the charm is active.

    Assume that the charm has been deployed and is running.
    """
    status = juju.status()
    assert status.apps[app].units[app + "/0"].is_active
    assert status.apps[app].units[app + "/1"].is_active


def test_scale_down(
    juju: jubilant.Juju,
    app: str,
    insights_address: str,
    requests_timeout: float,
):
    """Check that the charm can scale down without force."""
    juju.remove_unit(app, num_units=1)
    juju.wait(
        lambda status: jubilant.all_active(status, app) and jubilant.all_agents_idle(status, app)
    )

    response = requests.get(f"{insights_address}/version", timeout=requests_timeout)
    assert response.status_code == 200


def test_remove_application(
    juju: jubilant.Juju,
    app: str,
    insights_address: str,
    requests_timeout: float,
):
    """Check that the charm can be removed."""
    juju.remove_application(app, destroy_storage=True)
    juju.wait(lambda status: jubilant.all_active(status) and jubilant.all_agents_idle(status))

    try:
        response = requests.get(f"{insights_address}/version", timeout=requests_timeout)
        assert response.status_code == 404
    except (requests.Timeout, requests.ConnectionError):
        # Expected - application was removed, so connection should fail
        pass
    else:
        pytest.fail("Request should have failed, but it succeeded unexpectedly")
