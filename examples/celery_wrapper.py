"""Example: wrap a Django management command in a Celery task using
django-tee. Useful when you have a heavy management command you want
to fire off from a request handler or a celery-beat schedule, and
you want every invocation persisted.
"""

from __future__ import annotations

from celery import shared_task

from django_tee.core import execute


@shared_task
def run_send_daily_digest(batch_size: int = 500) -> int:
    """Run ``manage.py send_daily_digest`` with the given batch size,
    capture its output, and return the resulting Log row's primary key.
    """
    log = execute(
        [
            "manage.py",
            "send_daily_digest",
            f"--batch-size={batch_size}",
        ]
    )
    return log.pk
