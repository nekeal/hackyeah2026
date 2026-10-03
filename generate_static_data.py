# /// script
# dependencies = [
#     "osmnx",
#     "pyrosm",
#     "geopandas",
#     "requests",
#     "networkx",
#     "srtm.py"
# ]
# ///

"""
=============================================================================
MASTER SCRIPT: GENERATOR STATYCZNYCH DANYCH DLA HACKATHONU
=============================================================================
Ten skrypt to kompleksowe narzędzie do pobrania, przetworzenia i wygenerowania
wszystkich danych przestrzennych potrzebnych dla aplikacji mapowej (szczególnie
zoptymalizowanej pod dostępność dla wózków inwalidzkich w Krakowie).

Co pobiera i co generuje ten skrypt?

1. BAZA DANYCH OSM (Pobierana automatycznie jeśli brak)
   -> malopolskie-latest.osm.pbf (~100MB)
      Surowy i skompresowany zrzut całej bazy OpenStreetMap dla Małopolski.
      Służy nam jako potężne, lokalne źródło informacji bez odpytywania API.

2. WARSTWA PUNKTÓW DOCELOWYCH (POI)
   -> accessible_pois.geojson
      Skrypt skanuje PBF i wyciąga wyłącznie miejsca w granicach Krakowa, które
      zostały wyraźnie oflagowane jako dostępne (tag `wheelchair=yes`).
      Zastosowanie: Załadowanie jako pinezki na frontendzie lub do bazy Django.

3. GŁÓWNA SIATKA DROGOWA 3D DLA BACKENDU (ROUTING)
   -> city_network_3d.graphml
      Skrypt pobiera siatkę chodników i ścieżek (network="walk") przez OSMnx,
      a następnie w locie pobiera dane wysokościowe z API Open-Meteo.
      Dzięki temu każda ulica otrzymuje wbudowany atrybut `grade` (kąt nachylenia).
      Zastosowanie: Plik dla algorytmów (np. Dijkstry) by wyznaczać trasy unikające stromych górek.

4. WARSTWA DROGOWA 3D DLA FRONTENDU (WIZUALIZACJA)
   -> roads_3d.geojson
      Ten sam zbiór krawędzi drogowych co wyżej, ale zrzucony do formatu
      wektorowego. Posiada właściwości `grade` i `grade_abs`.
      Zastosowanie: Bezpośrednie wyrysowanie ścieżek na mapie frontendu (np.
      kolorując strome odcinki na czerwono).
=============================================================================
"""

from pathlib import Path

# =============================================================================
# MONKEY-PATCH: Naprawa błędu w integracji Geopandas 1.2.0 i Pyrosm
# (Geopandas wysypuje się przy pustych danych bez kolumny geometry).
import geopandas as gpd
import pandas as pd
import networkx as nx
import osmnx as ox
import requests
from pyrosm import OSM

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
FAST_MODE = False

print("========== GENEROWANIE STATYCZNYCH DANYCH DLA HACKATHONU ==========")
if FAST_MODE:
    print("[!] TRYB FAST_MODE: Będziemy przetwarzać tylko malutki wycinek miasta dla szybkiego testowania!")

# --- KROK 0: POBRANIE PLIKU PBF (JEŚLI NIE ISTNIEJE) ---
pbf_filename = "malopolskie-latest.osm.pbf"
# Sprawdzamy też stary plik dla pewności
if Path("malopolskie-261002.osm.pbf").exists() and not Path(pbf_filename).exists():
    pbf_filename = "malopolskie-261002.osm.pbf"

if not Path(pbf_filename).exists():
    print(f"\nKROK 0: Plik {pbf_filename} nie istnieje. Rozpoczynam pobieranie z Geofabrik (~100MB)...")
    url = "https://download.geofabrik.de/europe/poland/malopolskie-latest.osm.pbf"
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with Path(pbf_filename).open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(" Pobieranie zakończone!")
else:
    print(f"\nKROK 0: Plik {pbf_filename} znajduje się już na dysku. Pomijam pobieranie.")

# --- KROK 1: POBRANIE SIATKI DROGOWEJ (DLA PIESZYCH) ---
print("\nKROK 1: Pobieranie siatki ścieżek (walk) z LOKALNEGO pliku PBF (offline)...")
# Ramka (bounding box) Krakowa (MUSI BYĆ LISTĄ!)
if FAST_MODE:
    krakow_bbox = [19.93, 50.05, 19.95, 50.07]  # Rynek Główny
else:
    krakow_bbox = [19.79, 49.97, 20.22, 50.13]  # Cały Kraków
# Tworzymy nową instancję OSM
osm_network = OSM(pbf_filename)
osm_network.bounding_box = krakow_bbox

# Włączamy zachowywanie kluczowych tagów dla skrzyżowań (przeszkody i udogodnienia)
try:
    osm_network.keep_node_info_tags.extend(
        [
            # Przejścia i bariery fizyczne
            "crossing", "kerb", "tactile_paving", "barrier",
            # Dostępność ogólna
            "wheelchair", "elevator", "ramp", "ramp:wheelchair",
            "step_count", "handrail", "incline",
            # Infrastruktura węzłów (przystanki, place)
            "highway", "lit", "bench", "shelter", "covered", "level",
            # Systemy informacji pasażerskiej
            "departures_board", "departures_board:speech_output",
            "passenger_information_display",
        ]
    )
except AttributeError:
    pass

nodes_gdf, edges_gdf = osm_network.get_network(
    network_type="walking",
    nodes=True,
    extra_attributes=[
        # Nawierzchnia (kluczowe dla wózków — patrz surface_types_analysis.md)
        "surface", "smoothness",
        # Dostępność ogólna krawędzi
        "wheelchair", "incline", "ramp",
        # Dodatkowe atrybuty fizyczne
        "step_count", "handrail", "width",
        # Oświetlenie i komfort
        "lit",
        # Tagi barierowe
        "kerb", "tactile_paving",
    ],
)

# Przekształcamy na graf NetworkX
graph_nx = osm_network.to_graph(nodes_gdf, edges_gdf, graph_type="networkx", direction="oneway")
# OSMnx oczekuje MultiDiGraph, więc rzutujemy graf
graph = nx.MultiDiGraph(graph_nx)

# Współrzędne 'x' i 'y' są już automatycznie ustawione przez pyrosm.to_graph!

# Upewniamy się, że każda krawędź ma atrybut 'length' (długość w metrach)
graph = ox.distance.add_edge_lengths(graph)
print(f" Pobrano {len(graph.nodes)} węzłów drogowych bez łączenia się z internetem!")


# --- KROK 2: PUNKTY POI (WHEELCHAIR=YES) Z LOKALNEGO PLIKU PBF ---
print("\nKROK 2: Ekstrakcja przyjaznych POI (wheelchair=yes) z pliku PBF...")
try:
    osm = OSM(pbf_filename)

    # Customowy filtr wyciągający tylko obiekty z wheelchair=yes
    custom_filter = {"wheelchair": ["yes"]}

    # Pobieramy punkty (nodes), budynki/obszary (ways)
    pois = osm.get_data_by_custom_criteria(
        custom_filter=custom_filter, keep_nodes=True, keep_ways=True, keep_relations=False
    )

    # Ograniczamy dane z całego województwa tylko do ramki (bounding box) Krakowa (zdefiniowanej wyżej)
    pois_krakow = pois.cx[krakow_bbox[0] : krakow_bbox[2], krakow_bbox[1] : krakow_bbox[3]]

    pois_krakow.to_file("accessible_pois.geojson", driver="GeoJSON")
    print(f" Zapisano {len(pois_krakow)} dostępnych punktów POI dla Krakowa do 'accessible_pois.geojson'")
except Exception as e:
    print(f"Błąd podczas ekstrakcji POI: {e}")



# --- KROK 2.5: EKSTRAKCJA SZCZEGÓŁÓW DOSTĘPNOŚCI (KRAWĘŻNIKI, PRZEJŚCIA, TACTILE PAVING) ---
print("\nKROK 2.5: Ekstrakcja szczegółów dostępności (kerb/crossing/tactile_paving) z pliku PBF...")
try:
    osm_det = OSM(pbf_filename)
    custom_filter_det = {
        "kerb": [True, "raised", "lowered", "flush", "rolled", "no", "unknown"],
        "crossing": [True, "unmarked", "zebra", "marked", "traffic_signals", "island", "no"],
        "tactile_paving": [True, "yes", "no", "partial", "unknown"],
        # Nowe kategorie z analizy tagów dostępności
        "elevator": [True, "yes"],           # windy — kluczowe przy level<0
        "lit": [True, "yes", "no"],          # oświetlenie przejść/platform
        "bench": [True, "yes", "no"],        # miejsca do siedzenia
        "shelter": [True, "yes", "no"],      # zadaszenia (przystanki)
    }

    det_list = []
    for key, values in custom_filter_det.items():
        try:
            res = osm_det.get_data_by_custom_criteria(
                custom_filter={key: values}, keep_nodes=True, keep_ways=True, keep_relations=False
            )
            if res is not None and len(res) > 0:
                det_list.append(res)
        except Exception:
            continue

    if det_list:
        details = gpd.GeoDataFrame(pd.concat(det_list, ignore_index=True, sort=False))
    else:
        details = gpd.GeoDataFrame()

    if len(details) > 0:
        details_krakow = details.cx[krakow_bbox[0] : krakow_bbox[2], krakow_bbox[1] : krakow_bbox[3]]
    else:
        details_krakow = details

    def _det_type(row):
        has_kerb = bool(row.get("kerb"))
        has_cross = bool(row.get("crossing"))
        has_tact = bool(row.get("tactile_paving"))
        flags = sum([1 if has_kerb else 0, 1 if has_cross else 0, 1 if has_tact else 0])
        if flags >= 2:
            return "mixed"
        if has_kerb:
            return "kerb"
        if has_cross:
            return "crossing"
        if has_tact:
            return "tactile_paving"
        return "other"

    if len(details_krakow) > 0:
        details_krakow = details_krakow.copy()
        details_krakow["type"] = details_krakow.apply(_det_type, axis=1)
        details_krakow["osm_type"] = details_krakow["geometry"].apply(
            lambda g: "node" if g.geom_type == "Point" else ("way" if g.geom_type in ("LineString", "MultiLineString") else "unknown")
        )
        keep_cols = [
            "osm_id",
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
            # Identyfikacja
            "name",
            "highway",
            "tags",
            "geometry",
        ]
        for c in keep_cols:
            if c not in details_krakow.columns:
                details_krakow[c] = None
        details_krakow = details_krakow[keep_cols].drop_duplicates(subset=["osm_type", "osm_id"], keep="first")

    details_krakow.to_file("accessibility_details.geojson", driver="GeoJSON")
    print(f" Zapisano {len(details_krakow)} szczegółów dostępności do 'accessibility_details.geojson'")
except Exception as e:
    print(f"Błąd podczas ekstrakcji szczegółów dostępności: {e}")

# --- KROK 3: DODANIE WYSOKOŚCI 3D DO SIATKI ---
print("\nKROK 3: Pobieranie wysokości 3D z modelu SRTM (offline)...")
try:
    import srtm

    elevation_data = srtm.get_data()

    for node_id, data in graph.nodes(data=True):
        lat = data.get("y", data.get("lat"))
        lon = data.get("x", data.get("lon"))

        alt = elevation_data.get_elevation(lat, lon)
        graph.nodes[node_id]["elevation"] = float(alt) if alt is not None else 0.0

    print(" Sukces! Dodano współrzędne Z (wysokość) do węzłów.")
except Exception as e:
    print(f" Błąd SRTM: {e}. Graf nie będzie miał poprawnych wysokości.")
    for node_id in graph.nodes():
        graph.nodes[node_id]["elevation"] = 0.0


# --- KROK 4: OBLICZANIE KĄTÓW NACHYLENIA ---
print("\nKROK 4: Obliczanie kątów nachylenia (grade) na podstawie różnicy wzniesień...")
graph = ox.elevation.add_edge_grades(graph)


# --- KROK 4.5: OBLICZANIE KOSZTÓW DOSTĘPNOŚCI (ACCESSIBILITY PENALTY) ---
print("\nKROK 4.5: Obliczanie mnożnika trudności (accessibility_penalty) z wytycznych...")
for _, _, _, data in graph.edges(keys=True, data=True):
    penalty = 1.0

    # 1. Nawierzchnia (surface) — wg surface_types_analysis.md
    surface = str(data.get("surface", "")).lower()
    # 🔴 Ekstremalne przeszkody (mnożnik ∞ lub bardzo wysoki)
    if surface in ["sand", "mud"]:
        penalty *= 5.0  # Niemal nieprzejezdne, wózek grzęźnie
    elif surface in ["pebblestone", "stepping_stones", "metal_grid"]:
        penalty *= 4.0  # Wysokie ryzyko utknięcia / upadku
    elif surface in ["cobblestone", "unhewn_cobblestone"]:
        penalty *= 3.0  # Kocie łby — ból i ryzyko wywrócenia
    # 🟡 Wyboiste i trudne
    elif surface in ["sett", "gravel", "grass_paver"]:
        penalty *= 2.5  # Duże opory toczenia
    elif surface in ["dirt", "earth", "ground", "unpaved", "fine_gravel"]:
        penalty *= 2.0  # Zależy od pogody, trudne przy wilgoci
    elif surface in ["grass"]:
        penalty *= 2.0  # Miękkie, trudne dla małych kółek
    # 🟢 Dobre (brak kary)
    # asphalt, paving_stones, paved, concrete, compacted, concrete:plates -> penalty=1.0

    # 2. Gładkość (smoothness) — doprecyzowanie ponad surface
    smoothness = str(data.get("smoothness", "")).lower()
    if smoothness in ["horrible", "very_bad"]:
        penalty *= 3.0
    elif smoothness in ["bad"]:
        penalty *= 2.0
    elif smoothness in ["intermediate"]:
        penalty *= 1.5
    # excellent, good -> brak kary

    # 3. Schody (highway=steps)
    highway = str(data.get("highway", "")).lower()
    if highway == "steps":
        step_count = int(data.get("step_count", 0) or 0)
        has_elevator = data.get("elevator") == "yes"
        has_ramp = data.get("ramp") == "yes" or data.get("ramp:wheelchair") == "yes"
        has_handrail = data.get("handrail") == "yes"
        if has_elevator:
            penalty *= 1.5   # Winda dostępna — opóźnienie oczekiwania
        elif has_ramp:
            penalty *= 2.0   # Rampa — wymaga wysiłku, ale przejezdna
        elif has_handrail and step_count <= 3:
            penalty *= 5.0   # Mało stopni z poręczą — trudne, ale możliwe
        else:
            penalty *= 100.0  # Schody bez udogodnień = blokada dla wózka!

    # 4. Kąt nachylenia (grade_abs z kroku 4)
    grade_abs = float(data.get("grade_abs", 0.0))
    if grade_abs > 0.12:
        penalty *= 5.0   # >12% — praktycznie nie do pokonania bez asysty
    elif grade_abs > 0.08:
        penalty *= 3.0   # >8%  — stromy podjazd, bardzo trudny
    elif grade_abs > 0.05:
        penalty *= 1.5   # 5–8% — odczuwalny wysiłek

    # 5. Oświetlenie (lit) — opcjonalny mnożnik dla trybu nocnego
    # Nie zmienia kosztu domyślnie, ale zapisujemy jako atrybut do filtrowania na frontendzie
    data["lit"] = str(data.get("lit", ""))

    # Zakładamy, że cost = length * penalty
    length = float(data.get("length", 1.0))
    data["accessibility_penalty"] = penalty
    data["accessibility_cost"] = length * penalty

# --- KROK 5: ZAPISYWANIE WYNIKÓW ---
print("\nKROK 5: Zapisywanie grafu oraz GeoJSONów...")
# Główny graf dla algorytmów backendowych
ox.save_graphml(graph, filepath="city_network_3d.graphml")
print(" Zapisano 'city_network_3d.graphml'")

# Osobny eksport krawędzi do GeoJSONa, żeby frontend/mapa łatwo mogła pokolorować strome chodniki na czerwono
gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)
# Aby GeoJSON mógł się zapisać, musimy usunąć kolumny będące listami (np. osmid czasem jest listą)
allowed_edge_cols = [
    "geometry",
    "grade",
    "grade_abs",
    "length",
    "highway",
    "name",
    "surface",
    "smoothness",
    "wheelchair",
    "incline",
    "ramp",
    "ramp:wheelchair",
    "step_count",
    "handrail",
    "width",
    "kerb",
    "tactile_paving",
    "lit",
    "accessibility_penalty",
    "accessibility_cost",
]
for col in gdf_edges.columns:
    if col not in allowed_edge_cols:
        gdf_edges = gdf_edges.drop(columns=[col])

# Rzutujemy pozostałe wartości tekstowe na string by uniknąć problemów z listami
for col in gdf_edges.columns:
    if col != "geometry":
        gdf_edges[col] = gdf_edges[col].astype(str)

gdf_edges.to_file("roads_3d.geojson", driver="GeoJSON")
print(" Zapisano 'roads_3d.geojson' dla Frontendu")

print("\n========== ZAKOŃCZONO SUKCESEM! ==========")
