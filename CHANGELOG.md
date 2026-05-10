# Changelog

All notable changes to django-tee will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
