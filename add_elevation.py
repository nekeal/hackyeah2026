# /// script
# dependencies = [
#     "osmnx",
# ]
# ///

import time

import osmnx as ox
import requests

print("Wczytywanie płaskiej mapy Krakowa (city_network.osm)...")
graph = ox.graph_from_xml("city_network.osm")

print(f"Wczytano {len(graph.nodes)} węzłów. Pobieranie wysokości z darmowego API (Open-Meteo)...")
nodes = list(graph.nodes(data=True))
batch_size = 100

for i in range(0, len(nodes), batch_size):
    batch = nodes[i : i + batch_size]
    lats = ",".join([str(n[1]["y"]) for n in batch])
    lons = ",".join([str(n[1]["x"]) for n in batch])

    url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"
    try:
        response = requests.get(url, timeout=30).json()
        if "elevation" in response:
            for j, elevation in enumerate(response["elevation"]):
                nodes[i + j][1]["elevation"] = elevation
    except Exception as e:
        print(f"Błąd dla paczki {i}: {e}")

    # Progress
    if i % 5000 == 0:
        print(f"Pobrano {i}/{len(nodes)} węzłów...")
    time.sleep(0.05)  # lekki limit by nie przeciążyć darmowego API

print("Zapisywanie wysokości do grafu...")
for node_id, data in nodes:
    graph.nodes[node_id]["elevation"] = data.get("elevation", 0.0)

print("Obliczanie kątów nachylenia (grade) dla każdej ulicy i chodnika...")
graph = ox.elevation.add_edge_grades(graph)

print("Zapisywanie trójwymiarowej mapy do city_network_3d.graphml...")
ox.save_graphml(graph, filepath="city_network_3d.graphml")

print("Gotowe! Mapa ma teraz wyliczone kąty nachylenia.")
