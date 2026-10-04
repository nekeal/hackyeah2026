from __future__ import annotations

import ast
import re
from typing import Any

SURFACE_SMOOTH_PAVING = "smooth_paving"
SURFACE_ROUGH_STONE = "rough_stone"
SURFACE_OTHER_DIFFICULT = "other_difficult"
SURFACE_MODERATE = "moderate"
SURFACE_UNKNOWN = "unknown"

_SMOOTHNESS_GOOD = {"good", "excellent"}
_SMOOTHNESS_ROUGH = {"intermediate", "bad", "very_bad", "horrible", "very_horrible", "impassable"}
_ROUGH_STONE_SURFACES = {
    "cobblestone",
    "unhewn_cobblestone",
    "pebblestone",
    "stepping_stones",
    "metal_grid",
}
_OTHER_DIFFICULT_SURFACES = {
    "dirt",
    "earth",
    "fine_gravel",
    "grass",
    "grass_paver",
    "gravel",
    "ground",
    "mud",
    "sand",
    "unpaved",
}
_SMOOTH_PAVING_SURFACES = {
    "asphalt",
    "compacted",
    "concrete",
    "concrete:plates",
    "paved",
    "paving_stones",
}


def _parse_surface_values(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        values: list[str] = []
        for item in value:
            values.extend(_parse_surface_values(item))
        return list(dict.fromkeys(values))

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "[]"}:
        return []

    if text.startswith(("[", "(")) and text.endswith(("]", ")")):
        try:
            return _parse_surface_values(ast.literal_eval(text))
        except ValueError, SyntaxError:
            pass

    return [part.strip().lower() for part in re.split(r"\s*/\s*|\s*,\s*|\s*;\s*", text) if part.strip()]


def classify_surface(surface: Any, smoothness: Any = None) -> str:
    """Classify a segment for wheelchair routing without treating unknown as safe."""
    surfaces = _parse_surface_values(surface)
    if not surfaces:
        return SURFACE_UNKNOWN

    smoothness_value = str(smoothness or "").strip().lower()
    if any(value in _ROUGH_STONE_SURFACES for value in surfaces):
        return SURFACE_ROUGH_STONE

    if "sett" in surfaces:
        if smoothness_value in _SMOOTHNESS_GOOD:
            return SURFACE_SMOOTH_PAVING
        if smoothness_value in _SMOOTHNESS_ROUGH:
            return SURFACE_ROUGH_STONE
        # The material is known even when OSM does not provide its condition.
        # Keep it cautious, but do not reject it as sand, gravel, or soft ground.
        return SURFACE_MODERATE

    if any(value in _OTHER_DIFFICULT_SURFACES for value in surfaces):
        return SURFACE_OTHER_DIFFICULT

    if any(value in _SMOOTH_PAVING_SURFACES for value in surfaces):
        if smoothness_value in _SMOOTHNESS_ROUGH:
            return SURFACE_OTHER_DIFFICULT
        return SURFACE_SMOOTH_PAVING

    return SURFACE_UNKNOWN
