import json
from typing import Any

from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services import NoRouteFoundError, calculate_route


def map_view(request: HttpRequest) -> HttpResponse:
    return render(request, "map/index.html")


def pois_view(request: HttpRequest) -> HttpResponse:
    return render(request, "map/pois.html")


def route_view(request: HttpRequest) -> HttpResponse:
    return render(request, "map/route.html")


def pois_geojson(request: HttpRequest) -> HttpResponseBase:
    filepath = settings.BASE_DIR / "accessible_pois.geojson"
    if not filepath.exists():
        raise Http404("Plik accessible_pois.geojson nie istnieje. Wygeneruj go skryptem generate_static_data.py")
    return FileResponse(filepath.open("rb"), content_type="application/geo+json")


def roads_geojson(request: HttpRequest) -> HttpResponseBase:
    filepath = settings.BASE_DIR / "roads_3d.geojson"
    if not filepath.exists():
        raise Http404("Plik roads_3d.geojson nie istnieje. Wygeneruj go najpierw skryptem generate_static_data.py")
    return FileResponse(filepath.open("rb"), content_type="application/geo+json")


def details_geojson(request: HttpRequest) -> HttpResponseBase:
    filepath = settings.BASE_DIR / "accessibility_details.geojson"
    if not filepath.exists():
        raise Http404("Plik accessibility_details.geojson nie istnieje. Wygeneruj go skryptem generate_static_data.py")
    return FileResponse(filepath.open("rb"), content_type="application/geo+json")


@csrf_exempt
def route_api(request: HttpRequest) -> JsonResponse:  # noqa: C901
    """API Endpoint for calculating accessible walking / wheelchair route."""
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Dozwolone metody to GET oraz POST."}, status=405)

    data: dict[str, Any] = {}
    if request.method == "POST":
        try:
            if request.body:
                data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError, UnicodeDecodeError:
            return JsonResponse({"error": "Nieprawidłowy ciąg znaków JSON w żądaniu."}, status=400)
    else:
        data = request.GET.dict()

    start = data.get("start")
    end = data.get("end")

    try:
        if isinstance(start, dict):
            start_lat = float(start["lat"])
            start_lon = float(start["lon"])
        elif isinstance(start, (list, tuple)) and len(start) >= 2:
            start_lat = float(start[0])
            start_lon = float(start[1])
        else:
            start_lat = float(data["start_lat"])
            start_lon = float(data["start_lon"])

        if isinstance(end, dict):
            end_lat = float(end["lat"])
            end_lon = float(end["lon"])
        elif isinstance(end, (list, tuple)) and len(end) >= 2:
            end_lat = float(end[0])
            end_lon = float(end[1])
        else:
            end_lat = float(data["end_lat"])
            end_lon = float(data["end_lon"])
    except KeyError, TypeError, ValueError, IndexError:
        return JsonResponse(
            {"error": "Wymagane współrzędne początkowe i końcowe (np. start: {lat, lon} lub start_lat, start_lon)."},
            status=400,
        )

    preferences = data.get("preferences", {})
    if not isinstance(preferences, dict):
        preferences = {}

    options: dict[str, Any] = {
        "max_slope": float(preferences.get("max_slope", data.get("max_slope", 6.0))),
        "allow_stairs": str(preferences.get("allow_stairs", data.get("allow_stairs", "false"))).lower()
        in ("true", "1", "yes"),
        "allow_ramps": str(preferences.get("allow_ramps", data.get("allow_ramps", "true"))).lower()
        in ("true", "1", "yes"),
        "allow_elevators": str(preferences.get("allow_elevators", data.get("allow_elevators", "true"))).lower()
        in ("true", "1", "yes"),
        "avoid_cobblestone": str(preferences.get("avoid_cobblestone", data.get("avoid_cobblestone", "true"))).lower()
        in ("true", "1", "yes"),
        "smooth_crossing": str(preferences.get("smooth_crossing", data.get("smooth_crossing", "true"))).lower()
        in ("true", "1", "yes"),
        "avoid_narrow": str(preferences.get("avoid_narrow", data.get("avoid_narrow", "false"))).lower()
        in ("true", "1", "yes"),
        "allow_relaxed": str(preferences.get("allow_relaxed", data.get("allow_relaxed", "true"))).lower()
        in ("true", "1", "yes"),
        "excluded_node_ids": data.get("excluded_node_ids", []),
        "excluded_edge_ids": data.get("excluded_edge_ids", []),
        "excluded_barriers": data.get("excluded_barriers", []),
    }

    try:
        route_result = calculate_route(start_lat, start_lon, end_lat, end_lon, options=options)
        return JsonResponse(route_result)
    except NoRouteFoundError as e:
        return JsonResponse({"error": str(e)}, status=422)
    except Exception as e:
        return JsonResponse({"error": f"Wystąpił błąd podczas obliczania trasy: {e}"}, status=500)
