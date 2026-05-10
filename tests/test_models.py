"""Tests for Log model basics."""

import pytest

from django_tee.models import Log


@pytest.mark.django_db
def test_log_str_includes_command_name():
    log = Log.objects.create(command_name="some_cmd", args=["a", "b"])
    s = str(log)
    assert "some_cmd" in s
    assert "ran on" in s


@pytest.mark.django_db
def test_log_default_ordering_newest_first():
    older = Log.objects.create(command_name="old")
    newer = Log.objects.create(command_name="new")

    qs = list(Log.objects.all())
    assert qs[0].pk == newer.pk
    assert qs[1].pk == older.pk
