from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render


def map_view(request):
    return render(request, "map/index.html")


def pois_view(request):
    return render(request, "map/pois.html")


def pois_geojson(request):
    filepath = settings.BASE_DIR / "accessible_pois.geojson"
    if not filepath.exists():
        raise Http404("Plik accessible_pois.geojson nie istnieje. Wygeneruj go skryptem generate_static_data.py")
    return FileResponse(filepath.open("rb"), content_type="application/geo+json")


def roads_geojson(request):
    # Serwowanie wygenerowanego statycznego geojsona z glownego katalogu projektu
    filepath = settings.BASE_DIR / "roads_3d.geojson"
    if not filepath.exists():
        raise Http404("Plik roads_3d.geojson nie istnieje. Wygeneruj go najpierw skryptem generate_static_data.py")

    return FileResponse(filepath.open("rb"), content_type="application/geo+json")
