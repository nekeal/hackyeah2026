# /// script
# dependencies = [
#     "osmnx",
#     "pyrosm",
#     "geopandas",
#     "requests",
#     "networkx",
#     "srtm.py",
#     "pyarrow",
#     "lxml"
# ]
# ///

"""
=============================================================================
MASTER SCRIPT: GENERATOR STATYCZNYCH DANYCH DLA HACKATHONU
=============================================================================
Ten skrypt to kompleksowe narzędzie do pobrania, przetworzenia i wygenerowania
wszystkich danych przestrzennych potrzebnych dla aplikacji mapowej (szczególnie
zoptymalizowanej pod dostępność dla wózków inwalidzkich w Krakowie).

Wydajność (zmierzone na malopolskie-*.osm.pbf, 193 MB):
  - pyrosm czyta PBF silnikiem `out_of_core` (dekodowanie równoległe + filtr
    na etapie dekodowania) zamiast wczytywać cały plik do pamięci.
  - KROK 0.5 przycina PBF do ramki Krakowa (jednorazowo, wynik jest cache'owany),
    dzięki czego każdy kolejny odczyt operuje na ~49 MB zamiast ~193 MB.
  - Wszystkie odczyty (siatka + POI + szczegóły dostępności) korzystają z JEDNEJ
    instancji `OSM`, a PBF jest dekodowany w sumie tylko dwa razy.

Co pobiera i co generuje ten skrypt?

1. BAZA DANYCH OSM (Pobierana automatycznie jeśli brak)
   -> malopolskie-latest.osm.pbf (~100MB)
      Surowy i skompresowany zrzut całej bazy OpenStreetMap dla Małopolski.
      Służy nam jako potężne, lokalne źródło informacji bez odpytywania API.

1.5. PRZYCIĘTY PLIK (jednorazowo, cache'owany)
   -> krakow-bbox-<minx>_<miny>_<maxx>_<maxy>.osm.pbf
      Wszystkie węzły i drogi w obrębie ramki Krakowa. Nie gubimy niczego —
      bbox jest identyczny z tym, który i tak narzucaliśmy przy odczycie.

2. WARSTWA PUNKTÓW DOCELOWYCH (POI)
   -> accessible_pois.geojson
      Miejsca w granicach Krakowa oflagowane jako dostępne (tag `wheelchair=yes`).
      Zastosowanie: pinezki na frontendzie.

3. GŁÓWNA SIATKA DROGOWA 3D DLA BACKENDU (ROUTING)
   -> city_network_3d.graphml
      Siatka chodników i ścieżek (network="walk") wzbogacona o wysokość z SRTM,
      dzięki czemu każda krawędź ma atrybut `grade` (kąt nachylenia).
      Zastosowanie: Dijkstra wyznaczające trasy unikające stromych górek.
      UWAGA dla backendu — osmnx traktuje `oneway` jako bool, a `accessibility_*`
      jako nieznany typ, więc po wczytaniu podaj typy własnych atrybutów:
          ox.load_graphml(
              "city_network_3d.graphml",
              edge_dtypes={"accessibility_cost": float, "accessibility_penalty": float},
          )
      i ważuj krawędzie po `accessibility_cost` albo `length`.

4. WARSTWA DROGOWA 3D DLA FRONTENDU (WIZUALIZACJA)
   -> roads_3d.geojson
      Ten sam zbiór krawędzi, ale w formacie wektorowym, z `grade` i `grade_abs`.

5. SZCZEGÓŁY DOSTĘPNOŚCI (przejścia, krawężniki, nawierzchnie dotykowe)
   -> accessibility_details.geojson
      Wszystkie obiekty w Krakowie mające którykolwiek z tagów: kerb, crossing,
      tactile_paving, elevator, lit, bench, shelter. Zbierane w tym samym
      odczycie co POI (jeden przebieg dekodowania zamiast ośmiu).

6. PROWADENCJA DANYCH
   -> data_provenance.json
      Źródło, data pozyskania i parametry wygenerowania (wymóg z REQUIREMENTS.md).
=============================================================================
"""

import json
import os
import time
from pathlib import Path

# =============================================================================
# MONKEY-PATCH: Naprawa błędu w integracji Geopandas 1.2.0 i Pyrosm
# (Geopandas wysypuje się przy pustych danych bez kolumny geometry).
import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import requests
from pyrosm import OSM
from pyrosm.pbf_export import crop_pbf

from hackyeah2026.map.surfaces import (
    SURFACE_OTHER_DIFFICULT,
    SURFACE_ROUGH_STONE,
    SURFACE_UNKNOWN,
    classify_surface,
)

original_init = gpd.GeoDataFrame.__init__


def patched_init(self, *args, **kwargs):
    try:
        original_init(self, *args, **kwargs)
    except ValueError as e:
        if "without a geometry column" in str(e):
            if "crs" in kwargs:
                kwargs.pop("crs")
            original_init(self, *args, **kwargs)
        else:
            raise


gpd.GeoDataFrame.__init__ = patched_init
# =============================================================================

# Ustaw na True, aby testować tylko mały wycinek (np. Rynek Główny) -> błyskawiczny feedback!
FAST_MODE = True  # keep always true

# Topologiczne upraszczenie siatki: 600k -> 214k węzłów, identyczna geometria
# i identyczne odległości, ale 3x szybszy zapis i routing. Węzły pośrednie nie
# niosą żadnych tagów, więc nie tracimy na nich informacji.
SIMPLIFY_GRAPH = True

# Ramka całego Krakowa (minx, miny, maxx, maxy) — MUSI BYĆ LISTĄ!
KRAKOW_BBOX = [19.79, 49.97, 20.22, 50.13]
RYNEK_GŁÓWNY_BBOX = [19.93, 50.05, 19.95, 50.07]  # Rynek Główny (tryb testowy)

PBF_FILENAME = "malopolskie-latest.osm.pbf"
LEGACY_PBF_FILENAME = "malopolskie-261002.osm.pbf"

# Tagi krawędzi, na których zależy nam przy routingu dla wózka.
EDGE_EXTRA_ATTRIBUTES = [
    # Nawierzchnia (kluczowe dla wózków — patrz surface_types_analysis.md)
    "surface",
    "smoothness",
    "surface_category",
    # Dostępność ogólna krawędzi
    "wheelchair",
    "incline",
    "ramp",
    # Dodatkowe atrybuty fizyczne
    "step_count",
    "handrail",
    "width",
    # Oświetlenie i komfort
    "lit",
    # Tagi barierowe
    "kerb",
    "tactile_paving",
]

# Klucze, na podstawie których budujemy warstwę szczegółów dostępności.
# Używamy formy Overpass `["klucz"]` (dopasowanie po samej obecności tagu),
# co daje SUPERSET dawniej używanych filtrów po wartościach, np. łapie też
# crossing=uncontrolled, lit=no czy tactile_paving=partial.
DETAIL_KEYS = ["kerb", "crossing", "tactile_paving", "elevator", "lit", "bench", "shelter"]

# Dodatkowe tagi wyciągane do kolumn dla warstw POI / szczegółów.
DETAIL_EXTRA_ATTRIBUTES = [
    "wheelchair",
    "level",
    "name",
    "highway",
    "elevator",
    "lit",
    "bench",
    "shelter",
    "departures_board",
    "departures_board:speech_output",
    "passenger_information_display",
    "kerb",
    "crossing",
    "tactile_paving",
    "ramp",
    "ramp:wheelchair",
    "surface",
    "smoothness",
    "incline",
    "step_count",
    "handrail",
    "width",
]

# Kolumny zostawiane w accessibility_details.geojson (w kolejności zapisu).
DETAIL_KEEP_COLUMNS = [
    "id",
    "osm_type",
    "type",
    # Tagi barierowe przejść
    "kerb",
    "crossing",
    "tactile_paving",
    # Dostępność ogólna
    "wheelchair",
    # Infrastruktura budynków / platform
    "elevator",
    "lit",
    "bench",
    "shelter",
    "level",
    # Informacja pasażerska
    "departures_board",
    "passenger_information_display",
    # Identyfikacja i opis nawierzchni
    "name",
    "highway",
    "ramp",
    "ramp:wheelchair",
    "surface",
    "smoothness",
    "incline",
    "step_count",
    "handrail",
    "width",
    # Metadane OSM (wymagane przez REQUIREMENTS.md — proweniencja danych)
    "timestamp",
    "version",
    "changeset",
    "tags",
    "geometry",
]

# Kolumny zostawiane w roads_3d.geojson. To warstwa WIZUALIZACYJNA dla frontendu,
# więc bez kolumny 'tags' (to duplikat poszczególnych kolumn, ~2x rozmiar pliku)
# i bez metadanych OSM — komplet danych źródłowych trzymają .graphml, POI,
# szczegóły dostępności i data_provenance.json.
ROADS_GEOJSON_COLUMNS = [
    "geometry",
    "length",
    # Identyfikacja krawędzi
    "highway",
    "name",
    "oneway",
    "bridge",
    "tunnel",
    "layer",
    "access",
    "foot",
    "sidewalk",
    # Nawierzchnia (kluczowe dla wózków — patrz surface_types_analysis.md)
    "surface",
    "smoothness",
    "tracktype",
    # Dostępność
    "wheelchair",
    "incline",
    "ramp",
    "ramp:wheelchair",
    "step_count",
    "handrail",
    "width",
    "lit",
    "kerb",
    "tactile_paving",
    # Nachylenie i koszt dostępności (liczone w krokach 4 i 4.5)
    "grade",
    "grade_abs",
    "accessibility_penalty",
    "accessibility_cost",
]

_START = time.monotonic()


def log(message: str) -> None:
    print(f"[{time.monotonic() - _START:7.1f}s] {message}", flush=True)


# --- KROK 0: PLIK PBF (JEŚLI NIE ISTNIEJE) ---
def resolve_source_pbf() -> Path:
    pbf = Path(PBF_FILENAME)
    legacy = Path(LEGACY_PBF_FILENAME)
    # Sprawdzamy też stary plik dla pewności
    if legacy.exists() and not pbf.exists():
        pbf = legacy

    if pbf.exists():
        log(f"KROK 0: Plik {pbf} znajduje się już na dysku. Pomijam pobieranie.")
        return pbf

    log(f"KROK 0: Plik {pbf} nie istnieje. Rozpoczynam pobieranie z Geofabrik (~100MB)...")
    url = "https://download.geofabrik.de/europe/poland/malopolskie-latest.osm.pbf"
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with pbf.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    log(" Pobieranie zakończone!")
    return pbf


# --- KROK 0.5: PRZYCIĘCIE PBF DO RAMKI KRAKOWA (jednorazowo) ---
def ensure_cropped_pbf(source: Path, bbox: list[float]) -> Path:
    target = Path("krakow-bbox-{}_{}_{}_{}.osm.pbf".format(*bbox))
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        log(f"KROK 0.5: {target} jest aktualny. Pomijam przycinanie.")
        return target

    log(f"KROK 0.5: Przycinam {source.name} do ramki Krakowa -> {target} (jednorazowo)...")
    # crop_pbf przyjmuje wyłącznie liczbę workerów (nie "auto" jak silnik out_of_core).
    crop_pbf(str(source), str(target), bounding_box=bbox, workers=os.cpu_count() or 1)
    log(f" Gotowe ({target.stat().st_size / 1e6:.0f} MB zamiast {source.stat().st_size / 1e6:.0f} MB).")
    return target


def open_osm(path: Path, bbox: list[float]) -> OSM:
    """Jedna instancja OSM obsługuje wszystkie odczyty (bbox + silnik streamingowy)."""
    return OSM(
        str(path),
        bounding_box=bbox,
        keep_metadata=True,  # timestamp/date weryfikacji per obiekt (REQUIREMENTS.md)
        engine="out_of_core",
        workers="auto",
    )


# --- KROK 1: SIATKA DROGOWA DLA PIESZYCH ---
def build_graph(osm: OSM) -> nx.MultiDiGraph:
    log("KROK 1: Pobieranie siatki ścieżek (walk) z lokalnego pliku PBF (offline)...")
    nodes_gdf, edges_gdf = osm.get_network(
        network_type="walking",
        nodes=True,
        extra_attributes=EDGE_EXTRA_ATTRIBUTES,
    )
    log(f" Pobrano {len(nodes_gdf)} węzłów i {len(edges_gdf)} krawędzi.")

    # network_type musi być podany jawnie: ścieżka out_of_core nie zapisuje
    # metadanej typu sieci, po której to_graph rozpoznaje kierunek krawędzi.
    graph_nx = osm.to_graph(
        nodes_gdf,
        edges_gdf,
        graph_type="networkx",
        direction="oneway",
        network_type="walking",
        simplify=SIMPLIFY_GRAPH,
    )
    graph = nx.MultiDiGraph(graph_nx)

    # Upewniamy się, że każda krawędź ma atrybut 'length' (długość w metrach)
    graph = ox.distance.add_edge_lengths(graph)
    log(f" Graf gotowy: {len(graph.nodes)} węzłów, {len(graph.edges)} krawędzi.")
    return graph


# --- KROK 2 + 2.5: POI I SZCZEGÓŁY DOSTĘPNOŚCI (JEDEN ODCZYT) ---
def extract_pois_and_details(osm: OSM) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    log("KROK 2+2.5: Ekstrakcja POI (wheelchair=yes) i szczegółów dostępności w jednym odczycie...")
    combined_filter = ['["wheelchair"="yes"]'] + [f'["{key}"]' for key in DETAIL_KEYS]
    frame = osm.get_data_by_custom_criteria(
        custom_filter=combined_filter,
        keep_nodes=True,
        keep_ways=True,
        keep_relations=False,
        extra_attributes=DETAIL_EXTRA_ATTRIBUTES,
    )
    log(f" Odczytano {len(frame)} obiektów pasujących do filtrów.")

    # POI: dokładnie to, co dawniej dawał osobny filtr po wheelchair=yes.
    pois = frame[frame["wheelchair"] == "yes"].copy()

    # Szczegóły: obiekty mające którykolwiek z tagów dostępności.
    present = pd.DataFrame({key: frame[key].notna() for key in DETAIL_KEYS if key in frame.columns})
    details = frame[present.any(axis=1)].copy()
    details = assign_detail_types(details)

    missing = [column for column in DETAIL_KEEP_COLUMNS if column not in details.columns]
    for column in missing:
        details[column] = None
    details = details[DETAIL_KEEP_COLUMNS].drop_duplicates(subset=["osm_type", "id"], keep="first")
    return pois, details


def assign_detail_types(details: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Wektorowa wersja dawnego .apply(axis=1) — przy 75k wierszy to duża różnica."""
    for key in ("kerb", "crossing", "tactile_paving"):
        if key not in details.columns:
            details[key] = None
    has_kerb = details["kerb"].notna()
    has_crossing = details["crossing"].notna()
    has_tactile = details["tactile_paving"].notna()
    flags = has_kerb.astype("int8") + has_crossing.astype("int8") + has_tactile.astype("int8")

    detail_type = pd.Series("other", index=details.index, dtype=object)
    detail_type[has_kerb] = "kerb"
    detail_type[has_crossing] = "crossing"
    detail_type[has_tactile] = "tactile_paving"
    detail_type[flags >= 2] = "mixed"
    details["type"] = detail_type
    return details


# --- KROK 3: WYSOKOŚCI ---
def add_elevations(graph: nx.MultiDiGraph) -> None:
    log("KROK 3: Pobieranie wysokości 3D z modelu SRTM (offline)...")
    try:
        import srtm

        elevation_data = srtm.get_data()
        for node_id, data in graph.nodes(data=True):
            lat = data.get("y", data.get("lat"))
            lon = data.get("x", data.get("lon"))
            alt = elevation_data.get_elevation(lat, lon)
            graph.nodes[node_id]["elevation"] = float(alt) if alt is not None else 0.0
        log(" Sukces! Dodano współrzędne Z (wysokość) do węzłów.")

        # Wyboistość SRTM DEM 30m powoduje sztuczne skoki wysokości na płaskich ulicach miejskich.
        # Wygładzanie laplasowskie węzłów (3 iteracje) eliminuje szumy punktowe.
        log(" Wygładzanie laplasowskie wysokości węzłów (3 pasma)...")
        for _ in range(3):
            new_elevs = {}
            for node in graph.nodes():
                nbrs = list(graph.neighbors(node)) + list(graph.predecessors(node))
                if nbrs:
                    nbr_set = set(nbrs)
                    avg_alt = sum(float(graph.nodes[n].get("elevation", 0.0) or 0.0) for n in nbr_set) / len(nbr_set)
                    new_elevs[node] = 0.5 * float(graph.nodes[node].get("elevation", 0.0) or 0.0) + 0.5 * avg_alt
                else:
                    new_elevs[node] = float(graph.nodes[node].get("elevation", 0.0) or 0.0)
            for node, alt in new_elevs.items():
                graph.nodes[node]["elevation"] = alt
        log(" Zakończono wygładzanie wysokości węzłów.")
    except Exception as e:
        log(f" Błąd SRTM: {e}. Graf nie będzie miał poprawnych wysokości.")
        for node_id in graph.nodes():
            graph.nodes[node_id]["elevation"] = 0.0


# --- KROK 4: KĄTY NACHYLENIA I FILTROWANIE SZUMU ---
def add_grades(graph: nx.MultiDiGraph) -> None:
    log("KROK 4: Obliczanie kątów nachylenia (grade) na podstawie różnicy wzniesień...")
    ox.elevation.add_edge_grades(graph)

    fixed = 0
    cleaned_spikes = 0
    for u, v, _, data in graph.edges(keys=True, data=True):
        # 1. Czyszczenie wartości NaN / inf
        for key in ("grade", "grade_abs"):
            value = float(data.get(key, 0.0) or 0.0)
            if value != value or value in (float("inf"), float("-inf")):
                data[key] = 0.0
                fixed += 1

        length = float(data.get("length", 1.0) or 1.0)
        highway = str(data.get("highway", "")).lower()
        incline = data.get("incline")

        # 2. Dla schodów ustawiamy wysokie strome nachylenie (25%), by na mapie były zawsze CZERWONE
        if highway == "steps":
            data["grade"] = 0.25
            data["grade_abs"] = 0.25
            continue

        u_alt = float(graph.nodes[u].get("elevation", 0.0) or 0.0)
        v_alt = float(graph.nodes[v].get("elevation", 0.0) or 0.0)
        dz = abs(u_alt - v_alt)

        # 3. Usuwanie szumów wysokościowych DEM ze zwykłych ścieżek/chodników
        raw_grade = abs(float(data.get("grade", 0.0) or 0.0))
        data["grade_abs"] = raw_grade

        if not incline:
            if raw_grade > 0.05:
                # Na płaskich terenach miejskich nachylenie >5% bez tagu incline/steps to w 100% szum SRTM
                if length < 30.0:
                    data["grade"] = 0.0
                    data["grade_abs"] = 0.0
                else:
                    clamped = min(dz / length, 0.03) if length > 0 else 0.0
                    is_pos = float(data.get("grade", 0.0) or 0.0) >= 0
                    data["grade"] = clamped if is_pos else -clamped
                    data["grade_abs"] = clamped
                cleaned_spikes += 1

    if fixed:
        log(f" Wyzerowano {fixed} wartości grade/grade_abs typu NaN.")
    log(f" Wyczyszczono/wygładzono {cleaned_spikes} fałszywych kolców nachylenia z szumu DEM.")


def is_missing(value: object) -> bool:
    """Brak tagu w OSM pyrosm zapisuje jako NaN — w GraphML-y ląduje wtedy litera 'nan'."""
    return value is None or (isinstance(value, float) and value != value)


# Atrybuty w grafie, których NIGDY nie usuwamy, nawet jeśli są puste.
PROTECTED_GRAPH_ATTRS = {
    "geometry",
    "x",
    "y",
    "elevation",
    "length",
    "grade",
    "grade_abs",
    "accessibility_penalty",
    "accessibility_cost",
    "osmid",
    "highway",
    "street_count",
    "u",
    "v",
}

# Metadane OSM, które tylko mnożą rozmiar pliku — proweniencja i tak jest
# w data_provenance.json (data pozyskania) oraz w 'timestamp' (data edycji w OSM).
DROP_GRAPH_ATTRS = {"tags", "version", "changeset", "visible"}


def normalize_oneway_for_graphml(graph: nx.MultiDiGraph) -> None:
    """OSM daje `oneway=yes`, a osmnx przy wczytywaniu GraphML oczekuje prawdziwego booleana.

    Bez tego `ox.load_graphml` wywala się na `Invalid literal for boolean: 'yes'`.
    Wartości nieprzekładalne ('reversible') usuwamy — kierunek i tak jest już
    zakodowany w samym grafie (to_graph rozbija krawędzie na kierunkowe).
    """
    truthy = {"yes", "true", "1", "-1"}
    falsy = {"no", "false", "0"}
    dropped = 0
    for _, _, _, data in graph.edges(keys=True, data=True):
        if "oneway" not in data:
            continue
        value = data["oneway"]
        if isinstance(value, bool):
            continue
        token = str(value).strip().lower()
        if token in truthy:
            data["oneway"] = True
        elif token in falsy:
            data["oneway"] = False
        else:
            del data["oneway"]
            dropped += 1
    if dropped:
        log(f" Usunięto {dropped} krawędzi z niejednoznacznym tagiem oneway.")


def prune_graph_for_saving(graph: nx.MultiDiGraph) -> None:
    """Wyrzuca puste atrybuty (NaN) i zduplikowane metadane przed zapisem.

    Bez tego krawędź pakuje ~44 atrybuty, z czego ~20 to `nan` za brakujący tag —
    setki megabajytów śmieci i wielokrotnie dłuższy zapis.
    """
    normalize_oneway_for_graphml(graph)
    removed = 0
    for _, data in graph.nodes(data=True):
        removable = [
            key
            for key, value in data.items()
            if key not in PROTECTED_GRAPH_ATTRS and (key in DROP_GRAPH_ATTRS or is_missing(value))
        ]
        for key in removable:
            del data[key]
        removed += len(removable)

    for _, _, _, data in graph.edges(keys=True, data=True):
        removable = [
            key
            for key, value in data.items()
            if key not in PROTECTED_GRAPH_ATTRS and (key in DROP_GRAPH_ATTRS or is_missing(value))
        ]
        for key in removable:
            del data[key]
        removed += len(removable)

    log(f" Usunięto {removed} pustych/niepotrzebnych atrybutów przed zapisem grafu.")


def as_int(value: object) -> int:
    """Znaczniki OSM bywają '12', 12.0 albo NaN — wszystkie traktujemy jak liczbę."""
    try:
        return int(float(value))  # type: ignore[arg-type]
    except TypeError, ValueError:
        return 0


# --- KROK 4.5: KOSZTY DOSTĘPNOŚCI ---
def add_accessibility_costs(graph: nx.MultiDiGraph) -> None:
    log("KROK 4.5: Obliczanie mnożnika trudności (accessibility_penalty) z wytycznych...")
    for _, _, _, data in graph.edges(keys=True, data=True):
        penalty = 1.0

        # 1. Nawierzchnia (surface + smoothness) — wspólna klasyfikacja routingu
        smoothness = data.get("smoothness")
        surface_category = classify_surface(data.get("surface"), smoothness)
        data["surface_category"] = surface_category

        if surface_category == SURFACE_UNKNOWN:
            penalty *= 100.0  # Brak danych nie oznacza dostępności.
        elif surface_category == SURFACE_ROUGH_STONE:
            penalty *= 3.0  # Nierówny bruk / kocie łby.
        elif surface_category == SURFACE_OTHER_DIFFICULT:
            penalty *= 4.0  # Piasek, żwir, błoto i inne trudne podłoża.

        # 3. Schody (highway=steps)
        if str(data.get("highway", "")).lower() == "steps":
            step_count = as_int(data.get("step_count"))
            has_elevator = data.get("elevator") == "yes"
            has_ramp = data.get("ramp") == "yes" or data.get("ramp:wheelchair") == "yes"
            has_handrail = data.get("handrail") == "yes"
            if has_elevator:
                penalty *= 1.5  # Winda dostępna — opóźnienie oczekiwania
            elif has_ramp:
                penalty *= 2.0  # Rampa — wymaga wysiłku, ale przejezdna
            elif has_handrail and step_count <= 3:
                penalty *= 5.0  # Mało stopni z poręczą — trudne, ale możliwe
            else:
                penalty *= 100.0  # Schody bez udogodnień = blokada dla wózka!

        # 4. Kąt nachylenia (grade_abs z kroku 4)
        grade_abs = float(data.get("grade_abs", 0.0))
        if grade_abs > 0.12:
            penalty *= 5.0  # >12% — praktycznie nie do pokonania bez asysty
        elif grade_abs > 0.08:
            penalty *= 3.0  # >8%  — stromy podjazd, bardzo trudny
        elif grade_abs > 0.05:
            penalty *= 1.5  # 5–8% — odczuwalny wysiłek

        # 5. Oświetlenie (lit) — nie zmienia kosztu, ale zapisujemy jako atrybut
        #    do filtrowania na frontendzie (tryb nocny).
        data["lit"] = _clean_val(data.get("lit")) or ""

        # Zakładamy, że cost = length * penalty
        length = float(data.get("length", 1.0))
        data["accessibility_penalty"] = penalty
        data["accessibility_cost"] = length * penalty


def _clean_val(v: object) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                import ast

                s_fix = s.replace("nan", "None").replace("NaN", "None")
                parsed = ast.literal_eval(s_fix)
                if isinstance(parsed, (list, tuple, set)):
                    return _clean_val(parsed)
            except Exception:
                pass
        if s.lower() in ["nan", "none", "<na>", "null", "", "[]"]:
            return None
        return s

    if isinstance(v, (list, tuple, set, np.ndarray, pd.Series)):
        for x in v:
            res = _clean_val(x)
            if res is not None:
                return res
        return None

    try:
        if pd.isna(v):  # type: ignore[arg-type]
            return None
    except Exception:
        pass

    s = str(v).strip()
    if s.lower() in ["nan", "none", "<na>", "null", ""]:
        return None
    return s


def clean_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    for col in gdf.columns:
        if col != "geometry":
            gdf[col] = [_clean_val(val) for val in gdf[col]]
    return gdf


# --- KROK 5: ZAPISYWANIE WYNIKÓW ---
def save_graph(graph: nx.MultiDiGraph) -> None:
    log("KROK 5: Zapisywanie GeoJSONów oraz grafu...")

    # 1. Eksport krawędzi do GeoJSONa dla Frontendu (błyskawiczny zapis w ~5s)
    _, gdf_edges = ox.graph_to_gdfs(graph)
    if "nodes" in gdf_edges.columns:
        gdf_edges = gdf_edges.drop(columns=["nodes"])
    gdf_edges = gdf_edges[[column for column in ROADS_GEOJSON_COLUMNS if column in gdf_edges.columns]]
    gdf_edges = clean_gdf(gdf_edges)

    gdf_edges.to_file("roads_3d.geojson", driver="GeoJSON")
    log(" Zapisano 'roads_3d.geojson' dla Frontendu")

    # 2. Eksport pełnego grafu GraphML dla algorytmów nawigacyjnych backendu
    prune_graph_for_saving(graph)
    ox.save_graphml(graph, filepath="city_network_3d.graphml")
    log(" Zapisano 'city_network_3d.graphml'")


def write_provenance(source: Path, cropped: Path, bbox: list[float], graph: nx.MultiDiGraph) -> None:
    """Proweniencja danych wymagana przez REQUIREMENTS.md (sekcja 'Data Provenance')."""
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": {
            "dataset": "OpenStreetMap",
            "provider": "Geofabrik",
            "file": source.name,
            "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(source.stat().st_mtime)),
            "extract_file": cropped.name,
        },
        "area": {
            "city": "Kraków",
            "bbox": bbox,
            "crs": "EPSG:4326",
        },
        "network": {
            "type": "walking",
            "type_original": "OSM",
            "simplified": SIMPLIFY_GRAPH,
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
        },
        "elevation": {"source": "SRTM (srtm-py)", "license": "NASA SRTM / public domain"},
        "outputs": [
            "accessible_pois.geojson",
            "accessibility_details.geojson",
            "roads_3d.geojson",
            "city_network_3d.graphml",
        ],
    }
    Path("data_provenance.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    log(" Zapisano 'data_provenance.json'")


def main() -> None:
    print("========== GENEROWANIE STATYCZNYCH DANYCH DLA HACKATHONU ==========")
    bbox = RYNEK_GŁÓWNY_BBOX if FAST_MODE else KRAKOW_BBOX
    if FAST_MODE:
        print("[!] TRYB FAST_MODE: przetwarzamy tylko malutki wycinek miasta dla szybkiego testowania!")

    source = resolve_source_pbf()
    cropped = ensure_cropped_pbf(source, bbox)

    # Jedna instancja OSM na cały przebieg: bbox + silnik out_of_core powodują,
    # że PBF jest dekodowany tylko dla elementów w ramce i tylko dla tagów,
    # których naprawdę potrzebujemy (zamiast wczytywać całe województwo).
    osm = open_osm(cropped, bbox)

    graph = build_graph(osm)
    add_elevations(graph)
    add_grades(graph)
    add_accessibility_costs(graph)

    pois, details = extract_pois_and_details(osm)
    pois = clean_gdf(pois)
    pois.to_file("accessible_pois.geojson", driver="GeoJSON")
    log(f" Zapisano {len(pois)} dostępnych punktów POI dla Krakowa do 'accessible_pois.geojson'")

    details = clean_gdf(details)
    details.to_file("accessibility_details.geojson", driver="GeoJSON")
    log(f" Zapisano {len(details)} szczegółów dostępności do 'accessibility_details.geojson'")

    save_graph(graph)
    write_provenance(source, cropped, bbox, graph)
    log("========== ZAKOŃCZONO SUKCESEM! ==========")


if __name__ == "__main__":
    main()
