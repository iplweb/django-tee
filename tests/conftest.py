"""Shared fixtures for the django-tee test suite."""

from __future__ import annotations

from io import StringIO

import pytest


@pytest.fixture
def stdout():
    return StringIO()


@pytest.fixture
def stderr():
    return StringIO()
