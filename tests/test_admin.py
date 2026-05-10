"""Smoke tests for the LogAdmin — ensures changelist and detail views
load and that add is forbidden (logs are written by the wrapper, not
by hand)."""

import pytest
from django.urls import reverse
from model_bakery import baker

from django_tee.models import Log


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin-password",
    )


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
def test_changelist_loads(admin_client):
    baker.make(Log)

    url = reverse("admin:tee_log_changelist")
    res = admin_client.get(url)
    assert res.status_code == 200


@pytest.mark.django_db
def test_changelist_search_loads(admin_client):
    baker.make(Log)

    url = reverse("admin:tee_log_changelist")
    res = admin_client.get(url + "?q=fafa")
    assert res.status_code == 200


@pytest.mark.django_db
def test_add_view_forbidden(admin_client):
    url = reverse("admin:tee_log_add")
    res = admin_client.get(url)
    assert res.status_code == 403


@pytest.mark.django_db
def test_changelist_renders_last_5_lines_with_traceback(admin_client):
    baker.make(
        Log,
        command_name="failed_job",
        traceback="line1\nline2\nline3\nline4\nline5\nline6\n",
    )

    url = reverse("admin:tee_log_changelist")
    res = admin_client.get(url)
    body = res.content.decode()
    assert "line6" in body
    assert "[...]" in body
