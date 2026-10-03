import json

import pytest
from django.urls import reverse

from hackyeah2026.map.selectors import clear_graph_cache


@pytest.mark.django_db
def test_route_api_post_valid(client):
    clear_graph_cache()
    url = reverse("map:route_api")
    payload = {
        "start": {"lat": 50.0617, "lon": 19.9373},
        "end": {"lat": 50.0645, "lon": 19.9413},
        "preferences": {
            "max_slope": 6.0,
            "allow_stairs": False,
            "avoid_cobblestone": True,
        },
    }
    response = client.post(url, data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert "geojson" in data
    assert "summary" in data
    assert "instructions" in data
    assert "provenance" in data


@pytest.mark.django_db
def test_route_api_invalid_coords(client):
    clear_graph_cache()
    url = reverse("map:route_api")
    payload = {"start": "invalid"}
    response = client.post(url, data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


@pytest.mark.django_db
def test_route_api_no_route(client):
    clear_graph_cache()
    url = reverse("map:route_api")
    payload = {
        "start": {"lat": 50.0617, "lon": 19.9373},
        "end": {"lat": 50.0617, "lon": 19.9373},
    }
    response = client.post(url, data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


@pytest.mark.django_db
def test_route_view_status_code(client):
    url = reverse("map:route")
    response = client.get(url)
    assert response.status_code == 200
