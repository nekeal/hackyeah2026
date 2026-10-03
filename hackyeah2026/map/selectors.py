import logging
from typing import Any

import networkx as nx  # type: ignore[import-untyped]
import numpy as np
import osmnx as ox
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cache for graph, node list, and coordinate lookup matrix
_GRAPH_CACHE: nx.MultiDiGraph | None = None
_NODE_IDS_CACHE: list[Any] | None = None
_COORDS_CACHE: np.ndarray | None = None


def get_routing_graph() -> tuple[nx.MultiDiGraph, list[Any], np.ndarray]:
    """Returns cached routing graph along with node IDs and coordinate matrix."""
    global _GRAPH_CACHE, _NODE_IDS_CACHE, _COORDS_CACHE

    if _GRAPH_CACHE is not None and _NODE_IDS_CACHE is not None and _COORDS_CACHE is not None:
        return _GRAPH_CACHE, _NODE_IDS_CACHE, _COORDS_CACHE

    filepath = settings.BASE_DIR / "city_network_3d.graphml"
    if not filepath.exists():
        raise FileNotFoundError(
            f"Plik siatki drogowej {filepath} nie istnieje. Wygeneruj go za pomocą generate_static_data.py"
        )

    logger.info("Wczytywanie grafu drogowego z %s...", filepath)
    graph = ox.load_graphml(
        filepath,
        edge_dtypes={
            "accessibility_cost": float,
            "accessibility_penalty": float,
            "grade": float,
            "grade_abs": float,
            "length": float,
        },
    )

    node_ids = list(graph.nodes)
    coords = np.array(
        [[graph.nodes[n].get("y", 0.0), graph.nodes[n].get("x", 0.0)] for n in node_ids], dtype=np.float64
    )

    _GRAPH_CACHE = graph
    _NODE_IDS_CACHE = node_ids
    _COORDS_CACHE = coords

    return _GRAPH_CACHE, _NODE_IDS_CACHE, _COORDS_CACHE


def clear_graph_cache() -> None:
    """Clears the graph cache (useful for tests or data updates)."""
    global _GRAPH_CACHE, _NODE_IDS_CACHE, _COORDS_CACHE
    _GRAPH_CACHE = None
    _NODE_IDS_CACHE = None
    _COORDS_CACHE = None


def find_nearest_node(lat: float, lon: float) -> tuple[Any, float]:
    """Finds the nearest graph node to given (lat, lon) coordinates."""
    _, node_ids, coords = get_routing_graph()
    diffs = coords - np.array([lat, lon], dtype=np.float64)
    dists = np.hypot(diffs[:, 0], diffs[:, 1])
    idx = int(np.argmin(dists))
    return node_ids[idx], float(dists[idx])


def get_node_coordinates(node_id: Any) -> tuple[float, float, float]:
    """Returns (lat, lon, elevation) for a given node ID."""
    graph, _, _ = get_routing_graph()
    node_data = graph.nodes[node_id]
    lat = float(node_data.get("y", 0.0))
    lon = float(node_data.get("x", 0.0))
    elevation = float(node_data.get("elevation", 0.0))
    return lat, lon, elevation
