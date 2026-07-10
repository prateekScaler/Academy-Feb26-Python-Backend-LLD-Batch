"""
django_db API tests — the CRUD contract and the ownership (authorization) rule.

Run from THIS folder:
    pip install django djangorestframework pytest-django
    pytest -v
"""

import pytest
from rest_framework.test import APIClient

from demoapp.models import Event


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_event_persists_and_returns_201(client, django_user_model):
    vipul = django_user_model.objects.create_user("vipul")
    client.force_authenticate(vipul)

    resp = client.post("/api/events/", {"title": "Standup"}, format="json")

    assert resp.status_code == 201                 # the HTTP contract
    assert resp.data["title"] == "Standup"
    assert Event.objects.count() == 1              # the real DB effect
    assert Event.objects.get().owner_id == vipul.id  # owner set to the caller


@pytest.mark.django_db
def test_anonymous_user_cannot_create(client):
    resp = client.post("/api/events/", {"title": "Standup"}, format="json")
    assert resp.status_code in (401, 403)          # not authenticated
    assert Event.objects.count() == 0


@pytest.mark.django_db
def test_the_owner_can_delete_their_event(client, django_user_model):
    vipul = django_user_model.objects.create_user("vipul")
    event = Event.objects.create(title="Standup", owner=vipul)   # vipul OWNS it
    client.force_authenticate(vipul)

    resp = client.delete(f"/api/events/{event.id}/")

    assert resp.status_code == 204                 # owner allowed -> deleted
    assert not Event.objects.filter(id=event.id).exists()


@pytest.mark.django_db
def test_a_non_owner_is_forbidden(client, django_user_model):
    vipul = django_user_model.objects.create_user("vipul")
    mallory = django_user_model.objects.create_user("mallory")
    event = Event.objects.create(title="Standup", owner=vipul)
    client.force_authenticate(mallory)             # NOT the owner

    resp = client.delete(f"/api/events/{event.id}/")

    assert resp.status_code == 403                 # forbidden
    assert Event.objects.filter(id=event.id).exists()   # still there
