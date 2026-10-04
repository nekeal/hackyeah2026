import json
from unittest.mock import patch

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
            "avoid_cobblestone": False,
            "avoid_difficult_surfaces": False,
            "allow_unknown_surfaces": True,
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
def test_route_api_passes_surface_preferences(client):
    url = reverse("map:route_api")
    payload = {
        "start": {"lat": 50.0617, "lon": 19.9373},
        "end": {"lat": 50.0645, "lon": 19.9413},
        "avoid_rough_stone": False,
        "allow_unknown_surfaces": True,
    }

    with patch("hackyeah2026.map.views.calculate_route", return_value={"summary": {}}) as calculate_route_mock:
        response = client.post(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    options = calculate_route_mock.call_args.kwargs["options"]
    assert options["avoid_cobblestone"] is False
    assert options["allow_unknown_surfaces"] is True
    assert options["allow_relaxed"] is False


@pytest.mark.django_db
def test_route_api_excludes_unknown_surfaces_by_default(client):
    url = reverse("map:route_api")
    payload = {
        "start": {"lat": 50.0617, "lon": 19.9373},
        "end": {"lat": 50.0645, "lon": 19.9413},
    }

    with patch("hackyeah2026.map.views.calculate_route", return_value={"summary": {}}) as calculate_route_mock:
        response = client.post(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    options = calculate_route_mock.call_args.kwargs["options"]
    assert options["allow_unknown_surfaces"] is False
    assert options["avoid_cobblestone"] is True


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


@pytest.mark.django_db
def test_geojson_endpoints_status_code(client):
    roads_url = reverse("map:roads_geojson")
    response = client.get(roads_url)
    assert response.status_code in (200, 404)  # 200 if file exists, 404 if dataset not generated yet

    geojson_url = reverse("map:geojson")
    response = client.get(geojson_url)
    assert response.status_code in (200, 404)
