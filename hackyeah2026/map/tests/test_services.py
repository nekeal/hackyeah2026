import math

import networkx as nx
import pytest

from hackyeah2026.map.selectors import clear_graph_cache
from hackyeah2026.map.services import (
    NoRouteFoundError,
    _build_weight_function,
    _calc_slope_penalty,
    _calc_surface_penalty,
    _clean_attribute_val,
    _find_path,
    calculate_route,
    translate_highway,
    translate_surface,
)
from hackyeah2026.map.surfaces import (
    SURFACE_MODERATE,
    SURFACE_ROUGH_STONE,
    SURFACE_SMOOTH_PAVING,
    SURFACE_UNKNOWN,
    classify_surface,
)


@pytest.mark.django_db
def test_translations():
    assert translate_surface("asphalt") == "Asfalt"
    assert translate_surface("sett") == "Bruk miejski"
    assert translate_surface("unknown_surface") == "Unknown_surface"
    assert translate_surface(None) == "Nieznana nawierzchnia (brak danych)"

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

    res = calculate_route(
        start_lat,
        start_lon,
        end_lat,
        end_lon,
        options={
            "max_slope": 8.0,
            "allow_stairs": False,
            "avoid_cobblestone": False,
            "avoid_difficult_surfaces": False,
            "allow_unknown_surfaces": True,
        },
    )

    assert "geojson" in res
    coords = res["geojson"]["geometry"]["coordinates"]
    assert len(coords) > 1
    assert coords[0][:2] == [round(start_lon, 6), round(start_lat, 6)]
    assert coords[-1][:2] == [round(end_lon, 6), round(end_lat, 6)]

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

    permissive_options = {
        "avoid_cobblestone": False,
        "avoid_difficult_surfaces": False,
        "allow_unknown_surfaces": True,
    }
    res1 = calculate_route(start_lat, start_lon, end_lat, end_lon, options=permissive_options)
    edges_to_exclude = res1["instructions"][0]["edge_ids"]

    res2 = calculate_route(
        start_lat,
        start_lon,
        end_lat,
        end_lon,
        options={**permissive_options, "excluded_edge_ids": edges_to_exclude},
    )
    assert res2["summary"]["total_distance_m"] > 0


def test_calc_slope_penalty():
    # Below or equal to limit -> allowed
    assert _calc_slope_penalty(0.05, 0.06) == 1.0
    assert _calc_slope_penalty(0.064, 0.06) == 1.2

    # Above limit + 0.5% tolerance -> blocked
    assert math.isinf(_calc_slope_penalty(0.11, 0.06))
    assert math.isinf(_calc_slope_penalty(0.07, 0.06))


def test_surface_classification_distinguishes_smooth_rough_and_unknown():
    assert classify_surface("paving_stones", "excellent") == SURFACE_SMOOTH_PAVING
    assert classify_surface("paving_stones", None) == SURFACE_SMOOTH_PAVING
    assert classify_surface("sett", "intermediate") == SURFACE_ROUGH_STONE
    assert classify_surface("sett", None) == SURFACE_MODERATE
    assert classify_surface(None, None) == SURFACE_UNKNOWN


def test_surface_penalty_blocks_rough_and_unknown_surfaces_by_default():
    assert _calc_surface_penalty("paving_stones", "excellent", True, True, False, set()) == 1.0
    assert math.isinf(_calc_surface_penalty("sett", "intermediate", True, True, False, set()))
    assert _calc_surface_penalty("sett", None, True, True, False, set()) == 1.0


def test_weight_function_excludes_unknown_surface_by_default():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, length=10.0, surface=None, smoothness=None)
    weight_fn = _build_weight_function({"avoid_cobblestone": True})

    assert math.isinf(weight_fn(1, 2, graph[1][2]))

    allowed_weight_fn = _build_weight_function(
        {"avoid_cobblestone": True, "avoid_difficult_surfaces": True, "allow_unknown_surfaces": True}
    )
    assert allowed_weight_fn(1, 2, graph[1][2]) == 10.0


def test_unknown_surface_never_enters_strict_or_relaxed_route():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, length=10.0, surface=None, smoothness=None)

    with pytest.raises(NoRouteFoundError):
        _find_path(graph, 1, 2, {})

    with pytest.raises(NoRouteFoundError):
        _find_path(graph, 1, 2, {"allow_relaxed": True})


@pytest.mark.django_db
def test_calculate_route_stairs_avoidance():
    clear_graph_cache()
    # Route that has no stairs option
    res = calculate_route(
        50.0617,
        19.9373,
        50.0645,
        19.9413,
        options={
            "allow_stairs": False,
            "avoid_cobblestone": False,
            "avoid_difficult_surfaces": False,
            "allow_unknown_surfaces": True,
        },
    )
    assert res["summary"]["is_relaxed"] is False
    assert not any(inst.get("has_stairs") for inst in res["instructions"])

    # Route that requires stairs when no step-free path exists
    res_stairs = calculate_route(
        50.05958,
        19.93703,
        50.05923,
        19.93728,
        options={
            "allow_stairs": False,
            "allow_relaxed": True,
            "avoid_cobblestone": False,
            "avoid_difficult_surfaces": False,
            "allow_unknown_surfaces": True,
        },
    )
    assert res_stairs["summary"]["is_relaxed"] is True
    assert res_stairs["summary"]["relaxed_warning"] is not None


@pytest.mark.django_db
def test_calculate_route_allow_relaxed_false():
    clear_graph_cache()
    # Strict mode: when no strict path exists, raise NoRouteFoundError
    with pytest.raises(NoRouteFoundError, match="100% bez barier"):
        calculate_route(
            50.05958,
            19.93703,
            50.05923,
            19.93728,
            options={"allow_stairs": False, "allow_relaxed": False},
        )


@pytest.mark.django_db
def test_calculate_route_relaxed_fallback_for_short_city_route():
    clear_graph_cache()
    result = calculate_route(
        50.06113,
        19.93669,
        50.05933,
        19.93633,
        options={"allow_relaxed": True},
    )

    assert result["summary"]["is_relaxed"] is True
    assert result["summary"]["total_distance_m"] > 0
    assert result["summary"]["barrier_counts"]["unknown_surface"] == 0


@pytest.mark.django_db
def test_calculate_route_data_status():
    clear_graph_cache()
    res = calculate_route(
        50.0617,
        19.9373,
        50.0645,
        19.9413,
        options={
            "avoid_cobblestone": False,
            "avoid_difficult_surfaces": False,
            "allow_unknown_surfaces": True,
        },
    )
    for inst in res["instructions"]:
        assert "data_status" in inst
        assert "has_missing_data" in inst
        assert inst["data_status"] in ("verified", "unknown", "unverified", "demo")
