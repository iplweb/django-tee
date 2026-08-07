# Changelog

All notable changes to django-tee will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for Django 6.1: added to the CI test matrix (Python 3.12 and
  3.13 only — Django 6.1 requires Python 3.12+), plus the
  `Framework :: Django :: 6.1` Trove classifier and the README
  compatibility matrix.

## [0.2.0] - 2026-05-10

### Added

- Pluggable error-reporting backends (`django_tee.backends`). Rollbar
  is no longer a special case — it sits alongside a new built-in
  Sentry backend, and custom callables can be plugged in via the
  new `DJANGO_TEE_ERROR_BACKENDS` Django setting (entries are either
  built-in names or dotted paths).
- Sentry integration via `pip install "django-tee[sentry]"` —
  exceptions are forwarded to `sentry_sdk.capture_exception`.
- New `all-backends` extra: `pip install "django-tee[all-backends]"`
  installs both Rollbar and Sentry SDKs.
- Test coverage for backend dispatch (autodetect, explicit setting,
  custom callable, failing-backend isolation).

### Changed

- `django_tee.core.execute()` now fans the exception out to every
  configured backend instead of the previous hard-coded `rollbar`
  call. With no settings and no SDKs installed, behavior is
  unchanged. With only `rollbar` installed, behavior is unchanged.
- A backend that itself raises while reporting no longer breaks
  other backends or masks the wrapped command's traceback — failures
  are swallowed per backend.

## [0.1.0] - 2026-05-10

### Added

- Initial public release.
- Extracted from the [bpp](https://github.com/iplweb/bpp) project,
  where it had been in use since 2021.
- `python manage.py tee <command> [args...]` wrapper.
- Programmatic `django_tee.core.execute(argv)`.
- `django_tee.models.Log` admin (read-only).
- Optional `rollbar` integration via `pip install
  "django-tee[rollbar]"`.
- Test suite running against PostgreSQL via testcontainers.

### Notes

- The Django app label is `tee` (not `django_tee`) so that
  installations that previously had a hand-rolled `tee` app inlined
  in their project (e.g. bpp) can drop in `django-tee` without
  renaming tables or rewriting `django_migrations` rows.
