# Route Planner Panel Adjustments

## Scope

Adjust the route planner sidebar without changing routing behavior or backend APIs.

## UI Changes

1. Move `Wyznacz Dostepna Trase` directly below the start and destination coordinate form so the primary action remains visible before the optional settings.
2. Make `Preferencje Dostepnosci` a collapsible section, closed by default.
3. Make `Widok Nawierzchni Ulic w Tle` a collapsible section, closed by default.
4. Use native `details` and `summary` controls so both sections support mouse and keyboard interaction.
5. Remove the inner scroll container from `Wskazowki Trasy`; route instructions should extend naturally and use the sidebar's main scroll.

## Implementation

- Target template: `hackyeah2026/map/templates/map/route.html`.
- Keep the existing visual tokens, labels, controls, and route logic.
- Add accessible focus and expand/collapse affordances for the section summaries.
- Do not introduce backend changes or new dependencies for the UI.

## Visual Verification

Use the Playwright browser integration against the Docker server:

- URL: `http://localhost:8000/map/route/`
- Desktop viewport: confirm the primary action is immediately below the coordinate form.
- Mobile viewport: confirm the sidebar remains usable and the map is not obscured unexpectedly.
- Keyboard: focus each section summary, toggle it with Enter and Space, and verify the focus indicator.
- Route result: generate a route and confirm instructions use the sidebar's single scroll container.
- Long content: confirm there is no independent scrollbar inside the instructions list.

## Validation

- Run the route planner tests.
- Run `make quality-check`.
- Inspect the final desktop and mobile browser screenshots for layout regressions.
