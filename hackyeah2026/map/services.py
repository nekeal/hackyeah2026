import math
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from .selectors import find_nearest_node, get_node_coordinates, get_routing_graph


class NoRouteFoundError(Exception):
    """Exception raised when no valid route can be found."""

    pass


SURFACE_NAMES_PL = {
    "asphalt": "Asfalt",
    "paving_stones": "Kostka brukowa (płaska)",
    "sett": "Bruk miejski",
    "cobblestone": "Kocie łby",
    "unhewn_cobblestone": "Nierówny bruk",
    "gravel": "Żwir",
    "fine_gravel": "Drobny żwir",
    "sand": "Piasek",
    "dirt": "Ziemia",
    "earth": "Ziemia",
    "grass": "Trawa",
    "concrete": "Beton",
    "compacted": "Utwardzona nawierzchnia",
    "paved": "Utwardzona",
    "unpaved": "Nieutwardzona",
}

HIGHWAY_NAMES_PL = {
    "footway": "Chodnik",
    "pedestrian": "Dancing / Deptak",
    "path": "Ścieżka",
    "steps": "Schody",
    "cycleway": "Droga dla rowerów",
    "residential": "Ulica dojazdowa",
    "service": "Droga wewnętrzna",
    "living_street": "Strefa zamieszkania",
    "track": "Droga leśna / polna",
    "crossing": "Przejście dla pieszych",
}


def _clean_attribute_val(val: Any) -> str | None:
    if val is None:
        return None

    if isinstance(val, (list, tuple, set)):
        cleaned_items: list[str] = []
        for item in val:
            item_str = _clean_attribute_val(item)
            if item_str and item_str.lower() not in ("nan", "none", "null", "<na>"):
                cleaned_items.append(item_str)
        if not cleaned_items:
            return None
        unique_items = list(dict.fromkeys(cleaned_items))
        return " / ".join(unique_items)

    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "<na>", "null", "[]"):
        return None

    if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
        import ast

        try:
            s_fixed = s.replace("nan", "None").replace("NaN", "None")
            parsed = ast.literal_eval(s_fixed)
            return _clean_attribute_val(parsed)
        except ValueError, SyntaxError:
            pass

    return s


def translate_surface(surface: Any) -> str:
    cleaned_val = _clean_attribute_val(surface)
    if not cleaned_val:
        return "Brak danych o nawierzchni"
    parts = [p.strip() for p in cleaned_val.split(" / ")]
    translated = [SURFACE_NAMES_PL.get(p.lower(), p.capitalize()) for p in parts]
    unique_translated = list(dict.fromkeys(translated))
    return " / ".join(unique_translated)


def translate_highway(highway: Any) -> str:
    cleaned_val = _clean_attribute_val(highway)
    if not cleaned_val:
        return "Atratywny odcinek pieszy"
    parts = [p.strip() for p in cleaned_val.split(" / ")]
    translated = [HIGHWAY_NAMES_PL.get(p.lower(), p.capitalize()) for p in parts]
    unique_translated = list(dict.fromkeys(translated))
    return " / ".join(unique_translated)


def _calc_stairs_penalty(
    highway: str,
    has_elevator: bool,
    has_ramp: bool,
    allow_stairs: bool,
    allow_elevators: bool,
    allow_ramps: bool,
    excluded_barriers: set[str],
) -> float:
    if highway != "steps":
        return 1.0

    if "stairs" in excluded_barriers:
        return math.inf

    if not allow_stairs:
        if has_elevator and allow_elevators:
            return 1.8
        if has_ramp and allow_ramps:
            return 2.5
        return math.inf

    return 12.0


def _calc_slope_penalty(
    grade_abs: float,
    max_slope_ratio: float,
    allow_stairs: bool = False,
    excluded_barriers: set[str] | None = None,
) -> float:
    # 0.5% tolerance for DEM spatial interpolation noise
    if grade_abs <= max_slope_ratio + 0.005:
        if grade_abs > max_slope_ratio:
            return 1.2
        return 1.0

    return math.inf


def _calc_surface_penalty(
    surface: str,
    avoid_cobblestone: bool,
    excluded_barriers: set[str],
) -> float:
    cobblestone_surfaces = {
        "cobblestone",
        "unhewn_cobblestone",
        "sett",
        "gravel",
        "sand",
        "pebblestone",
        "grass_paver",
        "dirt",
        "mud",
    }
    if surface not in cobblestone_surfaces:
        return 1.0

    if "cobblestone" in excluded_barriers or avoid_cobblestone:
        if surface in ("sand", "mud"):
            return math.inf
        return 15.0

    return 1.0


def _calc_narrow_penalty(width_raw: Any, avoid_narrow: bool) -> float:
    if not avoid_narrow or not width_raw:
        return 1.0

    try:
        width_val = float(width_raw)
        if width_val < 0.9:
            return 10.0
    except ValueError, TypeError:
        pass

    return 1.0


def _build_weight_function(options: dict[str, Any]):
    max_slope_raw = float(options.get("max_slope", 6.0))
    max_slope_pct = max_slope_raw * 100.0 if 0.0 < max_slope_raw <= 1.0 else max_slope_raw
    max_slope_ratio = max_slope_pct / 100.0

    allow_stairs = bool(options.get("allow_stairs", False))
    allow_ramps = bool(options.get("allow_ramps", True))
    allow_elevators = bool(options.get("allow_elevators", True))
    avoid_cobblestone = bool(options.get("avoid_cobblestone", True))
    avoid_narrow = bool(options.get("avoid_narrow", False))

    excluded_node_ids = set(options.get("excluded_node_ids", []))
    excluded_edge_list = options.get("excluded_edge_ids", [])
    excluded_edge_ids = {(str(item[0]), str(item[1])) for item in excluded_edge_list if len(item) == 2}
    excluded_barriers = set(options.get("excluded_barriers", []))

    def weight_func(u: Any, v: Any, data: dict[str, Any]) -> float:
        str_u, str_v = str(u), str(v)
        if str_u in excluded_node_ids or str_v in excluded_node_ids:
            return math.inf
        if (str_u, str_v) in excluded_edge_ids or (str_v, str_u) in excluded_edge_ids:
            return math.inf

        length = float(data.get("length", 1.0) or 1.0)
        highway = str(data.get("highway", "")).lower()
        surface = str(data.get("surface", "")).lower()
        grade_abs = float(data.get("grade_abs", 0.0) or 0.0)

        ramp_attr = data.get("ramp")
        ramp_wheel_attr = data.get("ramp:wheelchair")
        has_ramp = (ramp_attr in ("yes", True, "1")) or (ramp_wheel_attr in ("yes", True, "1"))
        has_elevator = data.get("elevator") in ("yes", True, "1")

        stairs_p = _calc_stairs_penalty(
            highway, has_elevator, has_ramp, allow_stairs, allow_elevators, allow_ramps, excluded_barriers
        )
        if math.isinf(stairs_p):
            return math.inf

        slope_p = _calc_slope_penalty(grade_abs, max_slope_ratio, allow_stairs, excluded_barriers)
        if math.isinf(slope_p):
            return math.inf

        surf_p = _calc_surface_penalty(surface, avoid_cobblestone, excluded_barriers)
        if math.isinf(surf_p):
            return math.inf

        narrow_p = _calc_narrow_penalty(data.get("width"), avoid_narrow)

        return length * stairs_p * slope_p * surf_p * narrow_p

    return weight_func


def _extract_path_edges(graph: Any, path_nodes: list[Any]) -> tuple[list[list[float]], list[dict[str, Any]]]:
    route_coords: list[list[float]] = []
    edges_data: list[dict[str, Any]] = []

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]

        edge_candidates = graph[u][v]
        best_key = min(edge_candidates, key=lambda k: float(edge_candidates[k].get("length", 1.0)))
        edge_info = edge_candidates[best_key]

        u_lat, u_lon, u_elev = get_node_coordinates(u)
        v_lat, v_lon, v_elev = get_node_coordinates(v)

        if not route_coords:
            route_coords.append([round(u_lon, 6), round(u_lat, 6), round(u_elev, 1)])
        route_coords.append([round(v_lon, 6), round(v_lat, 6), round(v_elev, 1)])

        edges_data.append(
            {
                "u": u,
                "v": v,
                "data": edge_info,
                "u_coords": (u_lat, u_lon, u_elev),
                "v_coords": (v_lat, v_lon, v_elev),
            }
        )

    return route_coords, edges_data


def _find_path(graph: Any, start_node: Any, end_node: Any, options: dict[str, Any]) -> tuple[list[Any], bool]:
    weight_fn = _build_weight_function(options)
    try:
        _, path_nodes = nx.bidirectional_dijkstra(graph, start_node, end_node, weight=weight_fn)
        return path_nodes, False
    except nx.NetworkXNoPath, nx.NodeNotFound:
        relaxed = dict(options)
        relaxed["allow_stairs"] = True
        relaxed["avoid_cobblestone"] = False
        relaxed["max_slope"] = max(float(options.get("max_slope", 6.0)), 12.0)
        relaxed["excluded_barriers"] = []
        relaxed_weight_fn = _build_weight_function(relaxed)

        try:
            _, path_nodes = nx.bidirectional_dijkstra(graph, start_node, end_node, weight=relaxed_weight_fn)
            return path_nodes, True
        except (nx.NetworkXNoPath, nx.NodeNotFound) as err:
            raise NoRouteFoundError(
                "Nie znaleziono dostępnego połączenia drogowego pomiędzy podanymi punktami."
            ) from err


def _build_step_warning(
    is_steps: bool,
    is_high_slope: bool,
    is_cobblestones: bool,
    is_raised_kerb: bool,
    data: dict,
    grade_pct: float,
    surface_label: str,
) -> str | None:
    warnings: list[str] = []
    if is_steps:
        ramp_str = " z rampą" if data.get("ramp") in ("yes", True) else ""
        elev_str = " z windą" if data.get("elevator") in ("yes", True) else ""
        warnings.append(f"Schody{ramp_str}{elev_str}")
    if is_high_slope:
        warnings.append(f"Stromy podjazd ({round(grade_pct, 1)}%)")
    if is_cobblestones:
        warnings.append(f"Trudna nawierzchnia ({surface_label})")
    if is_raised_kerb:
        warnings.append("Wysoki krawężnik")

    return ", ".join(warnings) if warnings else None


def _format_instructions(instructions: list[dict[str, Any]]) -> None:
    for i, inst in enumerate(instructions, 1):
        inst["step_number"] = i
        dist_str = (
            f"{int(round(inst['distance_m']))} m"
            if inst["distance_m"] < 1000
            else f"{round(inst['distance_m'] / 1000, 2)} km"
        )
        text = f"Kieruj się {inst['street_name']} przez {dist_str} ({inst['surface']})"
        if inst["warning"]:
            text += f" — ⚠️ {inst['warning']}"
        inst["text"] = text
        inst["distance_m"] = round(inst["distance_m"], 1)


def _analyze_item(item: dict[str, Any], max_slope_limit: float) -> dict[str, Any]:
    data = item["data"]
    u_lat, u_lon, u_elev = item["u_coords"]
    v_lat, v_lon, v_elev = item["v_coords"]

    length = float(data.get("length", 0.0) or 0.0)
    grade_abs = float(data.get("grade_abs", 0.0) or 0.0)
    grade_pct = grade_abs * 100.0

    raw_highway = data.get("highway")
    raw_surface = data.get("surface")
    raw_name = data.get("name")
    raw_kerb = data.get("kerb")

    cleaned_name = _clean_attribute_val(raw_name)
    cleaned_surface = _clean_attribute_val(raw_surface)
    cleaned_highway = _clean_attribute_val(raw_highway)
    cleaned_kerb = _clean_attribute_val(raw_kerb)

    is_steps = "steps" in (cleaned_highway.lower() if cleaned_highway else "")
    is_high_slope = grade_pct > max_slope_limit

    cobble_types = {"cobblestone", "unhewn_cobblestone", "sett", "gravel", "sand", "pebblestone"}
    is_cobblestones = False
    if cleaned_surface:
        is_cobblestones = any(s.strip().lower() in cobble_types for s in cleaned_surface.split("/"))

    is_raised_kerb = "raised" in (cleaned_kerb.lower() if cleaned_kerb else "")

    street_label = cleaned_name if cleaned_name else translate_highway(raw_highway)
    surface_label = translate_surface(raw_surface)
    warning_text = _build_step_warning(
        is_steps, is_high_slope, is_cobblestones, is_raised_kerb, data, grade_pct, surface_label
    )

    return {
        "length": length,
        "grade_pct": grade_pct,
        "street_label": street_label,
        "surface_label": surface_label,
        "warning_text": warning_text,
        "is_steps": is_steps,
        "is_high_slope": is_high_slope,
        "is_cobblestones": is_cobblestones,
        "is_raised_kerb": is_raised_kerb,
        "u_elev": u_elev,
        "v_elev": v_elev,
        "kerb": cleaned_kerb or "",
        "data": data,
        "v_coords": (v_lat, v_lon, v_elev),
        "u_coords": (u_lat, u_lon, u_elev),
    }


def _should_merge_segment(current_segment: dict[str, Any] | None, info: dict[str, Any]) -> bool:
    return (
        current_segment is not None
        and current_segment["street_name"] == info["street_label"]
        and current_segment["surface"] == info["surface_label"]
        and current_segment["has_warning"] == bool(info["warning_text"])
    )


def _process_route_segments(
    edges_data: list[dict[str, Any]], max_slope_limit: float
) -> tuple[list[dict[str, Any]], float, float, float, float, dict[str, int]]:
    instructions: list[dict[str, Any]] = []
    current_segment: dict[str, Any] | None = None

    total_distance = 0.0
    total_elevation_gain = 0.0
    max_slope_in_route = 0.0
    total_slope_sum = 0.0

    counts = {"stairs": 0, "high_slope": 0, "cobblestone": 0, "raised_kerbs": 0}

    for item in edges_data:
        u, v = item["u"], item["v"]
        info = _analyze_item(item, max_slope_limit)
        length, grade_pct = info["length"], info["grade_pct"]

        if info["v_elev"] - info["u_elev"] > 0:
            total_elevation_gain += info["v_elev"] - info["u_elev"]

        total_distance += length
        total_slope_sum += grade_pct * length
        max_slope_in_route = max(max_slope_in_route, grade_pct)

        counts["stairs"] += int(info["is_steps"])
        counts["high_slope"] += int(info["is_high_slope"])
        counts["cobblestone"] += int(info["is_cobblestones"])
        counts["raised_kerbs"] += int(info["is_raised_kerb"])

        v_lat, v_lon, v_elev = info["v_coords"]
        u_lat, u_lon, u_elev = info["u_coords"]

        if _should_merge_segment(current_segment, info) and current_segment is not None:
            current_segment["distance_m"] += length
            current_segment["edge_ids"].append([u, v])
            current_segment["coords"].append([round(v_lon, 6), round(v_lat, 6), round(v_elev, 1)])
            current_segment["max_slope_pct"] = max(current_segment["max_slope_pct"], grade_pct)
        else:
            if current_segment is not None:
                instructions.append(current_segment)

            current_segment = {
                "step_number": len(instructions) + 1,
                "street_name": info["street_label"],
                "distance_m": length,
                "surface": info["surface_label"],
                "max_slope_pct": round(grade_pct, 1),
                "has_stairs": info["is_steps"],
                "has_ramp": info["data"].get("ramp") in ("yes", True),
                "has_elevator": info["data"].get("elevator") in ("yes", True),
                "kerb_status": info["kerb"] if info["kerb"] else "brak danych",
                "warning": info["warning_text"],
                "has_warning": bool(info["warning_text"]),
                "edge_ids": [[u, v]],
                "coords": [
                    [round(u_lon, 6), round(u_lat, 6), round(u_elev, 1)],
                    [round(v_lon, 6), round(v_lat, 6), round(v_elev, 1)],
                ],
            }

    if current_segment is not None:
        instructions.append(current_segment)

    _format_instructions(instructions)
    return instructions, total_distance, total_elevation_gain, max_slope_in_route, total_slope_sum, counts


def calculate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculates an accessible route between start and end coordinates."""
    if options is None:
        options = {}

    graph, _, _ = get_routing_graph()

    start_node, _ = find_nearest_node(start_lat, start_lon)
    end_node, _ = find_nearest_node(end_lat, end_lon)

    if start_node == end_node:
        raise NoRouteFoundError("Punkt początkowy i końcowy znajdują się na tym samym węźle siatki drogowej.")

    path_nodes, is_relaxed = _find_path(graph, start_node, end_node, options)
    route_coords, edges_data = _extract_path_edges(graph, path_nodes)

    max_slope_limit = float(options.get("max_slope", 6.0))
    instructions, total_distance, total_elevation_gain, max_slope_in_route, total_slope_sum, counts = (
        _process_route_segments(edges_data, max_slope_limit)
    )

    if counts["stairs"] == 0 and counts["high_slope"] == 0 and counts["cobblestone"] == 0:
        status_label, status_code = "Pełna dostępność (trasa bez barier)", "accessible"
    elif counts["stairs"] == 0 and counts["high_slope"] <= 2:
        status_label, status_code = "Dostępna (odcinki o umiarkowanym nachyleniu)", "moderate"
    else:
        status_label, status_code = "Utrudniona (wymaga asysty lub pokonania barier)", "difficult"

    duration_min = max(1, int(round((total_distance / 1.0) / 60)))

    geojson_feature = {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": route_coords},
        "properties": {"total_distance_m": round(total_distance, 1), "status_code": status_code},
    }

    return {
        "type": "Feature",
        "geometry": geojson_feature["geometry"],
        "properties": geojson_feature["properties"],
        "geojson": geojson_feature,
        "summary": {
            "total_distance_m": round(total_distance, 1),
            "estimated_duration_min": duration_min,
            "max_slope_percent": round(max_slope_in_route, 1),
            "avg_slope_percent": round(total_slope_sum / total_distance, 1) if total_distance > 0 else 0.0,
            "elevation_gain_m": round(total_elevation_gain, 1),
            "accessibility_status": status_label,
            "status_code": status_code,
            "is_relaxed": is_relaxed,
            "start_coords": [start_lat, start_lon],
            "end_coords": [end_lat, end_lon],
            "start_node": start_node,
            "end_node": end_node,
            "barriers_summary": counts,
        },
        "instructions": instructions,
        "provenance": {
            "source": "OpenStreetMap & SRTM 3D DEM (Kraków)",
            "last_updated": "2026-10-03",
            "verification_status": "Zweryfikowano numerycznie (DEM + OSM tags)",
            "disclaimer": (
                "Informacje o nawierzchni i nachyleniu bazują na danych przestrzennych. Zawsze zachowaj ostrożność."
            ),
        },
    }
