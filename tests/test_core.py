"""Integration tests for django_tee.core.execute and the `tee` command."""

import pytest
from django.core.management import call_command

from django_tee.models import Log


@pytest.fixture(autouse=True)
def _patch_close_all(mocker):
    """Django's BaseCommand.execute calls connections.close_all() in
    its finally branch. Inside the test runner that would close the
    connection that pytest-django is using to wrap the test in a
    transaction, breaking subsequent assertions. Patch it out for the
    duration of every test in this module."""
    mocker.patch("django.db.connections.close_all")


@pytest.mark.django_db
def test_tee_okay_records_success(stdout, stderr):
    call_command("tee", "tee_test_okay", stdout=stdout, stderr=stderr)

    log = Log.objects.first()
    assert log is not None
    assert log.finished_successfully is True
    assert log.traceback in (None, "")

    # Output is forwarded to the caller-supplied streams.
    assert "Used print()" in stdout.getvalue()
    assert "Used print() with file=self.stderr" in stderr.getvalue()


@pytest.mark.django_db
def test_tee_okay_persists_stdout_stderr(stdout, stderr):
    call_command("tee", "tee_test_okay", stdout=stdout, stderr=stderr)

    log = Log.objects.first()
    assert "wrote to stdout" in log.stdout
    assert "wrote to stderr" in log.stderr


@pytest.mark.django_db
def test_tee_exception_records_traceback(stdout, stderr):
    call_command("tee", "tee_test_exception", stdout=stdout, stderr=stderr)

    log = Log.objects.first()
    assert log.finished_successfully is False
    assert log.traceback
    assert "Exception risen..." in log.traceback


@pytest.mark.django_db
def test_tee_exception_still_captures_pre_exception_output(stdout, stderr):
    """An exception must NOT throw away the output emitted before it
    blew up — that output is exactly what an operator needs to debug."""
    call_command("tee", "tee_test_exception", stdout=stdout, stderr=stderr)

    log = Log.objects.first()
    assert "wrote to stdout" in log.stdout
    assert "wrote to stderr" in log.stderr


@pytest.mark.django_db
def test_tee_records_args(stdout, stderr):
    call_command(
        "tee",
        "tee_test_okay",
        stdout=stdout,
        stderr=stderr,
    )

    log = Log.objects.first()
    # First positional arg is the wrapped command name; remaining are
    # forwarded args (none in this case).
    assert log.command_name
    assert log.args == ["tee_test_okay"]


@pytest.mark.django_db
def test_tee_finished_on_set(stdout, stderr):
    call_command("tee", "tee_test_okay", stdout=stdout, stderr=stderr)

    log = Log.objects.first()
    assert log.finished_on is not None
    assert log.finished_on >= log.started_on
