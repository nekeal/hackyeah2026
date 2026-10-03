import math

import pytest

from hackyeah2026.map.selectors import clear_graph_cache
from hackyeah2026.map.services import (
    NoRouteFoundError,
    _calc_slope_penalty,
    _clean_attribute_val,
    calculate_route,
    translate_highway,
    translate_surface,
)


@pytest.mark.django_db
def test_translations():
    assert translate_surface("asphalt") == "Asfalt"
    assert translate_surface("sett") == "Bruk miejski"
    assert translate_surface("unknown_surface") == "Unknown_surface"
    assert translate_surface(None) == "Brak danych o nawierzchni"

    assert translate_highway("footway") == "Chodnik"
    assert translate_highway("steps") == "Schody"
    assert translate_highway(None) == "Atratywny odcinek pieszy"


def test_clean_attribute_val():
    assert _clean_attribute_val(None) is None
    assert _clean_attribute_val("nan") is None
    assert _clean_attribute_val(["Plac Mariacki", "Plac Mariacki", "nan", "Mały Rynek"]) == "Plac Mariacki / Mały Rynek"
    assert _clean_attribute_val("['paving_stones', 'paving_stones', 'paving_stones', 'sett']") == "paving_stones / sett"
    assert (
        translate_surface("['paving_stones', 'paving_stones', 'paving_stones', 'sett']")
        == "Kostka brukowa (płaska) / Bruk miejski"
    )


@pytest.mark.django_db
def test_calculate_route_valid():
    clear_graph_cache()
    start_lat, start_lon = 50.0617, 19.9373
    end_lat, end_lon = 50.0645, 19.9413

    res = calculate_route(start_lat, start_lon, end_lat, end_lon, options={"max_slope": 8.0, "allow_stairs": False})

    assert "geojson" in res
    assert res["geojson"]["type"] == "Feature"
    assert len(res["geojson"]["geometry"]["coordinates"]) > 1

    summary = res["summary"]
    assert summary["total_distance_m"] > 0
    assert summary["estimated_duration_min"] >= 1
    assert "accessibility_status" in summary

    instructions = res["instructions"]
    assert len(instructions) > 0
    assert "text" in instructions[0]

    provenance = res["provenance"]
    assert "source" in provenance
    assert provenance["verification_status"] == "Zweryfikowano numerycznie (DEM + OSM tags)"


@pytest.mark.django_db
def test_calculate_route_same_start_end():
    clear_graph_cache()
    start_lat, start_lon = 50.0617, 19.9373
    with pytest.raises(NoRouteFoundError, match="tym samym"):
        calculate_route(start_lat, start_lon, start_lat, start_lon)


@pytest.mark.django_db
def test_calculate_route_exclusions():
    clear_graph_cache()
    start_lat, start_lon = 50.0617, 19.9373
    end_lat, end_lon = 50.0645, 19.9413

    res1 = calculate_route(start_lat, start_lon, end_lat, end_lon)
    edges_to_exclude = res1["instructions"][0]["edge_ids"]

    res2 = calculate_route(start_lat, start_lon, end_lat, end_lon, options={"excluded_edge_ids": edges_to_exclude})
    assert res2["summary"]["total_distance_m"] > 0


def test_calc_slope_penalty():
    # Below or equal to limit -> allowed
    assert _calc_slope_penalty(0.05, 0.06) == 1.0
    assert _calc_slope_penalty(0.064, 0.06) == 1.2

    # Above limit + 0.5% tolerance -> blocked
    assert math.isinf(_calc_slope_penalty(0.11, 0.06))
    assert math.isinf(_calc_slope_penalty(0.07, 0.06))
