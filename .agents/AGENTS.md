# AI Agent Guidelines for HackYeah2026

This project is a multi-agent, multi-person hackathon project. To prevent conflicts, merge issues, and ensure a high standard of code, all AI agents MUST strictly adhere to the following architectural and behavioral rules:

> **CRITICAL**: Before starting any feature, you MUST read `REQUIREMENTS.md` to ensure your design complies with the Hackathon's strict evaluation criteria (WCAG accessibility, data provenance, etc.).

## 1. Modular Monolith Architecture
- **Vertical Slices**: All new features must be placed into independent, domain-driven Django apps (e.g., `accounts`, `rentals`, `catalog`).
- **No Direct DB Mutations in APIs**: Views and API endpoints (`apis.py` or `views.py`) must never call `.save()`, `.create()`, or `.update()`. They must delegate to a function in `services.py`.
- **Cross-App Communication**: If App A needs data from App B, App A must **not** query App B's models directly. Instead, App A must call a function exposed in App B's `selectors.py` (for read logic) or `services.py` (for write logic).

## 2. File Structure Constraints
Each Django app MUST follow this specific file layout to reduce merge conflicts:
- `models.py`: STRICTLY database fields and constraints. **No business logic.**
- `services.py`: All business logic and write operations (creating/updating/deleting records).
- `selectors.py`: All read operations and complex database queries (fetching records).
- `apis.py` / `views.py` (or `apis/` / `views/` packages): Only parsing requests, delegating to services/selectors, and returning responses. If there are multiple unrelated classes or functions, split them into a Python package (e.g., `views/museums.py`, `views/tracks.py`, `views/__init__.py`).
- `tests/` (Directory): Isolated test files (e.g., `test_models.py`, `test_services.py`, `test_apis.py`). Do NOT use a single `tests.py` file.

## 3. Collaboration & Edits
- **Zero-Conflict Global Edits**: When registering a new app or URL route, append it cleanly to the end of `INSTALLED_APPS` (in `settings/base.py` or similar) or `urlpatterns` (in `urls.py`) to minimize git conflicts. Do not unnecessarily reformat global files.
- **TDD is Mandatory**: Whenever you create a new feature in `services.py` or `apis.py`, you MUST create the corresponding isolated test file in the `tests/` directory and ensure `uv run pytest` passes.
- **Validation**: Before concluding any task, ALWAYS run `make quality-check` (which runs `ruff format`, `ruff check`, and `mypy`) to ensure your code matches the strict repository rules. Fix any errors before stopping.

## 4. Static Data & Pipelines
- **Do not commit raw datasets**: Large `.osm`, `.osm.pbf`, `.graphml`, `.geojson`, or `.tif` files MUST be strictly added to `.gitignore`. They bloat the git repository.
- **Reproducibility**: Any data transformation must be codified into a single pipeline script (e.g. `generate_static_data.py`) so anyone on the team can regenerate the data locally with one command. Scripts should automatically download missing data.
- **Offline processing**: Prefer processing local datasets (like `.pbf` using `osmium`/`pyrosm`) over repeatedly hitting unstable public APIs (like Overpass API) to avoid timeout blocks during development.

## 4. Static Data & Pipelines
- **Do not commit raw datasets**: Large `.osm`, `.osm.pbf`, `.graphml`, `.geojson`, or `.tif` files MUST be strictly added to `.gitignore`. They bloat the git repository.
- **Reproducibility**: Any data transformation must be codified into a single pipeline script (e.g. `generate_static_data.py`) so anyone on the team can regenerate the data locally with one command. Scripts should automatically download missing data.
- **Offline processing**: Prefer processing local datasets (like `.pbf` using `osmium`/`pyrosm`) over repeatedly hitting unstable public APIs (like Overpass API) to avoid timeout blocks during development.
