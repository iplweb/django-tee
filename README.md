# django-tee

[![tests](https://github.com/iplweb/django-tee/actions/workflows/test.yml/badge.svg)](https://github.com/iplweb/django-tee/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-tee.svg)](https://pypi.org/project/django-tee/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-tee.svg)](https://pypi.org/project/django-tee/)
[![Django versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1%20%7C%205.2-blue)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Run a Django management command and capture its `stdout`, `stderr` and
any traceback into the database — like Unix `tee(1)`, but for cron jobs.

The output **also still lands on the underlying terminal**, so an
operator running the wrapper interactively keeps seeing the output
scroll by. The captured rows live in a single Django model (`Log`),
browseable through Django admin.

## Why

Cron jobs and systemd timers fail silently more often than anyone
likes to admit. By the time someone notices, the output is gone — the
wrapper script forgot to redirect, the log rotated, or `MAILTO` was
never set up.

`django-tee` gives you a Django-native, queryable record of what each
job emitted, when it ran, whether it crashed, and what its traceback
was — without changing the command itself. Wrap any existing
management command:

```bash
python manage.py tee my_command --any --args you --want
```

…and the output is both printed *and* saved.

## Features

- Wraps **any** Django management command — no changes to the command
  itself.
- Captures `stdout`, `stderr`, and `traceback` (on exception).
- Records start time, end time, and success / failure.
- Browseable & searchable through Django admin (read-only — logs are
  written by the wrapper, not by hand).
- Optional integration with [Rollbar](https://rollbar.com/) — if
  `rollbar` is installed and configured, exceptions are also reported
  there before being recorded.
- Output is forwarded to the original `stdout` / `stderr` *and*
  persisted, so interactive runs still feel normal.

## Installation

Using [uv](https://docs.astral.sh/uv/):

```bash
uv add django-tee
```

Using pip:

```bash
pip install django-tee
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_tee",
]
```

Then run migrations:

```bash
python manage.py migrate
```

> The Django app label is `tee` (not `django_tee`) for backward
> compatibility with installations that previously had a hand-rolled
> `tee` app inlined in their project. Tables are named `tee_log`,
> admin URLs are under `/admin/tee/log/`. The Python import path is
> `django_tee` regardless.

### Optional: Rollbar integration

```bash
pip install "django-tee[rollbar]"
```

If `rollbar` is importable and you've initialised it in your project
(see the [rollbar-pyrollbar
docs](https://docs.rollbar.com/docs/django)), exceptions raised by
the wrapped command are reported to Rollbar in addition to being
recorded in the `Log` row. If `rollbar` is not installed, this is a
no-op — no `try/except ImportError` needed in your code.

## Usage

### As a CLI wrapper

```bash
python manage.py tee <command_name> [args...]
```

Examples:

```bash
# Wrap a one-off:
python manage.py tee clearsessions

# Wrap your nightly batch job:
python manage.py tee send_daily_digest --batch-size=500

# In crontab:
0 4 * * * cd /srv/myapp && /srv/myapp/.venv/bin/python manage.py tee send_daily_digest >> /var/log/myapp/cron.log 2>&1
```

Each invocation creates one `Log` row. Browse them at
`/admin/tee/log/`.

### Programmatically

```python
from django_tee.core import execute

execute(["manage.py", "send_daily_digest", "--batch-size=500"])
```

`execute()` returns the persisted `Log` instance, so you can inspect
the result inline:

```python
from django_tee.core import execute

log = execute(["manage.py", "rebuild_search_index"])
if log.finished_successfully:
    print("rebuild OK")
else:
    print("rebuild FAILED:", log.traceback)
```

### Querying logs

```python
from django_tee.models import Log

# Latest failure of a given job:
last_fail = (
    Log.objects
    .filter(command_name__contains="send_daily_digest",
            finished_successfully=False)
    .order_by("-started_on")
    .first()
)

# Long-running invocations:
from django.db.models import F
slow = Log.objects.filter(
    finished_on__isnull=False,
).annotate(duration=F("finished_on") - F("started_on")).order_by("-duration")[:10]

# Anything that ran in the last hour:
from django.utils import timezone
from datetime import timedelta
recent = Log.objects.filter(
    started_on__gte=timezone.now() - timedelta(hours=1),
)
```

### Pruning old logs

There's no built-in retention — `Log.objects.filter(started_on__lt=...).delete()`
works fine, run it from a cron job (wrapped, of course):

```python
# myapp/management/commands/prune_tee_logs.py
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_tee.models import Log


class Command(BaseCommand):
    help = "Delete tee log rows older than --days days (default: 30)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)

    def handle(self, days, **opts):
        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = Log.objects.filter(started_on__lt=cutoff).delete()
        self.stdout.write(f"Deleted {deleted} tee log rows.")
```

Then:

```bash
python manage.py tee prune_tee_logs --days=90
```

…which itself records a (small) audit trail.

## Compatibility

| django-tee | Python      | Django               |
| ---------- | ----------- | -------------------- |
| 0.1.x      | 3.10 – 3.13 | 4.2, 5.0, 5.1, 5.2   |

Backend: PostgreSQL is the primary target (the `args` column is
`JSONField` and the project has historically run only on Postgres).
SQLite *should* work for `JSONField` since Django 3.1 but is not part
of the CI matrix — file an issue if you need it.

## Development

```bash
git clone https://github.com/iplweb/django-tee
cd django-tee
uv venv
uv pip install -e ".[test,dev]"
pre-commit install
uv run pytest
```

The test suite spins up a real PostgreSQL container via
[testcontainers](https://testcontainers-python.readthedocs.io/) — you
need a working Docker daemon.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

Originally extracted from
[bpp](https://github.com/iplweb/bpp) (Bibliografia Publikacji
Pracownikow), where it had been quietly recording the output of
nightly import jobs since 2021.
