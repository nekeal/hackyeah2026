# /// script
# dependencies = [
#     "osmnx",
# ]
# ///

import osmnx as ox

# 1. Konfiguracja OSMnx
ox.settings.all_oneway = True

# Dodanie tagów, które chcemy zachować na węzłach grafu drogowego (np. ułatwienia dostępu)
ox.settings.useful_tags_node.extend([
    "amenity", "wheelchair", "name", "kerb", "tactile_paving", "crossing", "tourism"
])

place_name = "Kraków, Poland"

print(f"Pobieranie nieuproszczonego grafu dla {place_name}...")
# 2. Pobieranie grafu
# (Używamy network_type="all" lub "drive", ale dla wózków inwalidzkich "walk" lub "all" może być lepsze)
graph = ox.graph_from_place(place_name, network_type="drive", simplify=False)

print("Zapisywanie grafu do city_network.osm...")
ox.save_graph_xml(graph, filepath="city_network.osm")

# 3. Pobieranie pełnych metadanych POI (Points of Interest) - np. muzea i wypożyczalnie
print("Pobieranie punktów POI (muzea, miejsca z wózkami)...")
# W OSMnx v2+ używamy features_from_place by pobrać dowolne obiekty z OSM (węzły, drogi, relacje)
tags_to_download = {
    "tourism": True,
    "amenity": True,
    "leisure": True,
    "shop": True,
    "historic": True,
    "wheelchair": True
}
pois = ox.features_from_place(place_name, tags=tags_to_download)

print("Zapisywanie POI do city_pois.geojson...")
# features_from_place zwraca GeoDataFrame z geopandas
pois.to_file("city_pois.geojson", driver="GeoJSON")

print("Sukces! Mapa i punkty POI zostały zapisane.")
