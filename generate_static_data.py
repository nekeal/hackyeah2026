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

import time
from pathlib import Path

# =============================================================================
# MONKEY-PATCH: Naprawa błędu w integracji Geopandas 1.2.0 i Pyrosm
# (Geopandas wysypuje się przy pustych danych bez kolumny geometry).
import geopandas as gpd
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
FAST_MODE = True

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
        ["crossing", "kerb", "tactile_paving", "highway", "wheelchair", "barrier", "elevator"]
    )
except AttributeError:
    pass

nodes_gdf, edges_gdf = osm_network.get_network(
    network_type="walking", nodes=True, extra_attributes=["surface", "smoothness", "wheelchair", "incline", "ramp"]
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
