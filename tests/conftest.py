# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""Module for pytest configuration."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--model",
        action="store",
        help="Juju model to use."
        "If not provided, a temporary model will be created for each test that requires one.",
    )
    parser.addoption(
        "--keep-models",
        action="store_true",
        default=False,
        help="Keep temporarily-created models",
    )
    parser.addoption(
        "--charm-file",
        action="store",
        help="Path to the charm file to deploy."
        "If not provided, the charm will be built from the current directory.",
    )
    parser.addoption(
        "--ubuntu-insights-server-image",
        action="store",
        help="The image to use for the ubuntu-insights-server resource. "
        "This image must be in an accessible registry.",
    )
