from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render


def map_view(request: HttpRequest) -> HttpResponse:
    return render(request, "map/index.html")


def pois_view(request: HttpRequest) -> HttpResponse:
    return render(request, "map/pois.html")


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
