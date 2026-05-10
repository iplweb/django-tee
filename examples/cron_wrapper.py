"""Example: programmatic use of django_tee from a cron-style wrapper.

Drop this file into your project, then schedule it with cron / systemd
/ Celery beat / whatever. Each run produces one ``django_tee.Log`` row
that you can browse in admin.

Usage from cron::

    0 4 * * * cd /srv/myapp && /srv/myapp/.venv/bin/python -m examples.cron_wrapper

(adjust the path; this file is illustrative — copy/adapt rather than
import directly).
"""

from __future__ import annotations

import os
import sys

# Adjust this to your project's settings module.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

import django  # noqa: E402  — must come after env var is set

django.setup()


def main() -> int:
    from django_tee.core import execute

    log = execute(
        [
            "manage.py",
            "send_daily_digest",
            "--batch-size=500",
        ]
    )

    if log.finished_successfully:
        return 0

    # Non-zero exit so cron's MAILTO (or the surrounding wrapper)
    # notices. The traceback is already in `log.traceback` and
    # browseable in admin — we don't need to print it again.
    sys.stderr.write(f"job failed; see /admin/tee/log/{log.pk}/change/ for details\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
