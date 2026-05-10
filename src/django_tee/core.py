import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout

from django.core.management import ManagementUtility
from django.utils import timezone

from django_tee.models import Log
from django_tee.utils import TeeIO

try:
    import rollbar  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised when rollbar is absent
    rollbar = None


def execute(argv, **kwargs):
    """Run a Django management command and persist its output to ``Log``.

    Calls the Django command described by ``argv`` (same shape as
    ``sys.argv`` — first element is the program name, second is the
    command name, remainder are command arguments) while capturing
    stdout, stderr and any traceback into a fresh ``django_tee.Log``
    row. Output also still lands on the underlying streams (terminal
    by default), so an operator running the wrapper interactively
    keeps seeing the output scroll by. Useful for cron / systemd-timer
    wrappers where you want a durable, queryable trail of what each
    job emitted.

    If the optional ``rollbar`` dependency is installed and
    configured, exceptions are also reported there before being
    recorded.
    """
    stdout = TeeIO(kwargs.get("stdout") if "stdout" in kwargs else sys.stdout)
    stderr = TeeIO(kwargs.get("stderr") if "stderr" in kwargs else sys.stderr)

    log = Log.objects.create(command_name=argv[0], args=argv[1:])

    try:
        with redirect_stderr(stderr):
            with redirect_stdout(stdout):
                try:
                    utility = ManagementUtility(argv)
                    utility.execute()
                    log.finished_successfully = True
                except Exception:
                    if rollbar is not None:
                        rollbar.report_exc_info(sys.exc_info())
                    log.finished_successfully = False
                    log.traceback = traceback.format_exc(limit=65535)
    finally:
        log.stdout = stdout.getvalue()
        log.stderr = stderr.getvalue()
        log.finished_on = timezone.now()
        log.save()

    return log
