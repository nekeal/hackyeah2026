from pathlib import Path
from unittest.mock import patch

import pytest

from hackyeah2026.map.selectors import (
    clear_graph_cache,
    find_nearest_node,
    get_node_coordinates,
    get_routing_graph,
)


@pytest.mark.django_db
def test_get_routing_graph_cached():
    clear_graph_cache()
    graph, node_ids, coords = get_routing_graph()
    assert graph is not None
    assert len(node_ids) > 0
    assert len(coords) == len(node_ids)

    graph2, node_ids2, _ = get_routing_graph()
    assert graph is graph2
    assert node_ids is node_ids2


@pytest.mark.django_db
def test_find_nearest_node():
    clear_graph_cache()
    node_id, dist = find_nearest_node(50.0617, 19.9373)
    assert node_id is not None
    assert dist >= 0.0

    lat, lon, elev = get_node_coordinates(node_id)
    assert isinstance(lat, float)
    assert isinstance(lon, float)
    assert isinstance(elev, float)


@pytest.mark.django_db
def test_get_routing_graph_file_not_found():
    clear_graph_cache()
    with patch("hackyeah2026.map.selectors.settings") as mock_settings:
        mock_settings.BASE_DIR = Path("/nonexistent/path")
        with pytest.raises(FileNotFoundError):
            get_routing_graph()
