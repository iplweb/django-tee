"""Tests for the pluggable error-reporting backends."""

from __future__ import annotations

import sys
import types

import pytest
from django.test import override_settings

from django_tee.backends import (
    BUILTIN_BACKENDS,
    RollbarBackend,
    SentryBackend,
    get_backends,
    report_exception,
)


def _exc_info():
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        return sys.exc_info()


def _install_fake_module(monkeypatch, name, **attrs):
    """Inject a fake top-level module into sys.modules for the test."""
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    monkeypatch.setitem(sys.modules, name, mod)
    return mod


# ---- per-backend availability ----------------------------------------------


def test_rollbar_backend_available_when_module_present(monkeypatch):
    _install_fake_module(monkeypatch, "rollbar", report_exc_info=lambda *a, **k: None)
    assert RollbarBackend().is_available() is True


def test_rollbar_backend_unavailable_when_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "rollbar", None)  # poisons import
    assert RollbarBackend().is_available() is False


def test_sentry_backend_available_when_module_present(monkeypatch):
    _install_fake_module(monkeypatch, "sentry_sdk", capture_exception=lambda *a: None)
    assert SentryBackend().is_available() is True


def test_sentry_backend_unavailable_when_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "sentry_sdk", None)
    assert SentryBackend().is_available() is False


# ---- per-backend report_exception ------------------------------------------


def test_rollbar_backend_forwards_exc_info(monkeypatch):
    captured = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: captured.append(info)
    )
    info = _exc_info()
    RollbarBackend().report_exception(info)
    assert captured == [info]


def test_sentry_backend_forwards_exception_instance(monkeypatch):
    captured = []
    _install_fake_module(
        monkeypatch, "sentry_sdk", capture_exception=lambda exc: captured.append(exc)
    )
    info = _exc_info()
    SentryBackend().report_exception(info)
    # Sentry's API takes the exception instance, not the tuple.
    assert captured == [info[1]]


# ---- dispatch via get_backends / report_exception --------------------------


def test_autodetect_picks_up_every_importable_backend(monkeypatch):
    calls = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: calls.append(("r", info))
    )
    _install_fake_module(
        monkeypatch,
        "sentry_sdk",
        capture_exception=lambda exc: calls.append(("s", exc)),
    )
    info = _exc_info()
    report_exception(info)
    kinds = sorted(name for name, _ in calls)
    assert kinds == ["r", "s"]


def test_autodetect_skips_uninstalled_backend(monkeypatch):
    calls = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: calls.append(info)
    )
    monkeypatch.setitem(sys.modules, "sentry_sdk", None)
    report_exception(_exc_info())
    assert len(calls) == 1


def test_no_backends_when_none_installed(monkeypatch):
    monkeypatch.setitem(sys.modules, "rollbar", None)
    monkeypatch.setitem(sys.modules, "sentry_sdk", None)
    # Must not raise even though no backend can run.
    report_exception(_exc_info())
    assert list(get_backends()) == []


def test_explicit_setting_restricts_to_named_backends(monkeypatch):
    calls = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: calls.append("r")
    )
    _install_fake_module(
        monkeypatch, "sentry_sdk", capture_exception=lambda exc: calls.append("s")
    )
    with override_settings(DJANGO_TEE_ERROR_BACKENDS=["sentry"]):
        report_exception(_exc_info())
    assert calls == ["s"]


def test_explicit_setting_supports_dotted_path(monkeypatch):
    calls = []

    def custom(exc_info):
        calls.append(exc_info)

    fake = _install_fake_module(monkeypatch, "fake_backend_pkg")
    fake.custom = custom

    with override_settings(DJANGO_TEE_ERROR_BACKENDS=["fake_backend_pkg.custom"]):
        info = _exc_info()
        report_exception(info)
    assert calls == [info]


def test_failing_backend_does_not_break_others(monkeypatch):
    calls = []

    def boom(exc_info):
        raise ValueError("backend exploded")

    _install_fake_module(
        monkeypatch, "sentry_sdk", capture_exception=lambda exc: calls.append("s")
    )
    fake = _install_fake_module(monkeypatch, "fake_broken_backend")
    fake.handler = boom

    with override_settings(
        DJANGO_TEE_ERROR_BACKENDS=["fake_broken_backend.handler", "sentry"]
    ):
        report_exception(_exc_info())

    # Sentry must have been reached even though the previous backend
    # raised.
    assert calls == ["s"]


def test_builtin_backends_registry_contains_rollbar_and_sentry():
    assert set(BUILTIN_BACKENDS) == {"rollbar", "sentry"}


# ---- integration with execute() --------------------------------------------


@pytest.fixture(autouse=True)
def _patch_close_all(mocker):
    mocker.patch("django.db.connections.close_all")


@pytest.mark.django_db
def test_execute_invokes_every_active_backend_on_exception(monkeypatch, stdout, stderr):
    seen = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: seen.append("rollbar")
    )
    _install_fake_module(
        monkeypatch, "sentry_sdk", capture_exception=lambda exc: seen.append("sentry")
    )

    from django.core.management import call_command

    call_command("tee", "tee_test_exception", stdout=stdout, stderr=stderr)

    assert sorted(seen) == ["rollbar", "sentry"]


@pytest.mark.django_db
def test_execute_does_not_call_backends_on_success(monkeypatch, stdout, stderr):
    seen = []
    _install_fake_module(
        monkeypatch, "rollbar", report_exc_info=lambda info: seen.append("rollbar")
    )
    _install_fake_module(
        monkeypatch, "sentry_sdk", capture_exception=lambda exc: seen.append("sentry")
    )

    from django.core.management import call_command

    call_command("tee", "tee_test_okay", stdout=stdout, stderr=stderr)

    assert seen == []
