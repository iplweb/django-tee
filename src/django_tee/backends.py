"""Pluggable error-reporting backends for django-tee.

When ``execute()`` catches an exception thrown by the wrapped command,
each active backend is given a chance to report it (Rollbar, Sentry,
…) before the traceback is persisted to the ``Log`` row.

Selection
---------

The set of active backends is controlled by the
``DJANGO_TEE_ERROR_BACKENDS`` Django setting. Each entry is either:

- a built-in name: ``"rollbar"`` or ``"sentry"``;
- a dotted import path to a callable taking ``(exc_info,)`` — useful
  for custom integrations.

If the setting is absent (or Django is not configured), every built-in
backend whose underlying SDK is importable is used. This preserves the
historical zero-config behavior: install ``rollbar`` and exceptions
flow there; install ``sentry-sdk`` and they flow to Sentry; install
both and they flow to both.

A backend whose SDK is not importable is silently skipped — no
``try/except ImportError`` is needed in user code.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable


class _Backend:
    """Minimal protocol implemented by every built-in backend."""

    name: str = ""

    def is_available(self) -> bool:
        raise NotImplementedError

    def report_exception(self, exc_info) -> None:
        raise NotImplementedError


class RollbarBackend(_Backend):
    """Forward exceptions to Rollbar via ``rollbar.report_exc_info``."""

    name = "rollbar"

    def is_available(self) -> bool:
        try:
            importlib.import_module("rollbar")
        except ImportError:
            return False
        return True

    def report_exception(self, exc_info) -> None:
        rollbar = importlib.import_module("rollbar")
        rollbar.report_exc_info(exc_info)


class SentryBackend(_Backend):
    """Forward exceptions to Sentry via ``sentry_sdk.capture_exception``.

    Relies on the host project having already initialised the Sentry
    SDK (typically with ``sentry_sdk.init(...)`` at startup). If the
    SDK is importable but uninitialised, ``capture_exception`` is a
    safe no-op.
    """

    name = "sentry"

    def is_available(self) -> bool:
        try:
            importlib.import_module("sentry_sdk")
        except ImportError:
            return False
        return True

    def report_exception(self, exc_info) -> None:
        sentry_sdk = importlib.import_module("sentry_sdk")
        # capture_exception accepts either an exception instance or an
        # exc_info tuple; passing the exception instance keeps the
        # behavior consistent across SDK versions.
        sentry_sdk.capture_exception(exc_info[1])


BUILTIN_BACKENDS: dict[str, type[_Backend]] = {
    "rollbar": RollbarBackend,
    "sentry": SentryBackend,
}


def _resolve_dotted(path: str) -> Callable:
    module_path, _, attr = path.rpartition(".")
    if not module_path:
        raise ImportError(f"Not a dotted path: {path!r}")
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def _settings_backends() -> list | None:
    """Return the configured backend list, or ``None`` if unset."""
    try:
        from django.conf import settings
    except ImportError:
        return None
    if not getattr(settings, "configured", False):
        return None
    return getattr(settings, "DJANGO_TEE_ERROR_BACKENDS", None)


def get_backends() -> Iterable[Callable]:
    """Yield callables that take ``exc_info`` and report it.

    Resolution order:

    1. If ``DJANGO_TEE_ERROR_BACKENDS`` is set, use exactly that list
       (entries that are not importable raise — explicit configuration
       should fail loudly).
    2. Otherwise, every built-in backend whose SDK can be imported is
       included.
    """
    configured = _settings_backends()

    if configured is None:
        for cls in BUILTIN_BACKENDS.values():
            backend = cls()
            if backend.is_available():
                yield backend.report_exception
        return

    for entry in configured:
        if entry in BUILTIN_BACKENDS:
            yield BUILTIN_BACKENDS[entry]().report_exception
        else:
            yield _resolve_dotted(entry)


def report_exception(exc_info) -> None:
    """Report ``exc_info`` to every active backend.

    A backend that raises while reporting must not mask the original
    exception or stop other backends from running, so failures are
    swallowed individually.
    """
    for handler in get_backends():
        try:
            handler(exc_info)
        except Exception:  # noqa: BLE001 — see docstring
            pass
