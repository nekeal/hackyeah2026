# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Główna grupa docelowa**: Osoby poruszające się na wózkach (ręcznych lub elektrycznych), podróżujące samodzielnie lub z asystentem, chcące bezpiecznie i niezależnie planować przejazdy po mieście (obszar demonstracji: centrum Krakowa).
- **Użytkownicy drugorzędni**: Opiekunowie i asystenci, lokalna społeczność zgłaszająca bariery, zarządcy obiektów oraz miasta wdrażające system.

## Product Purpose

Przejezdni to aplikacja ułatwiająca osobom poruszającym się na wózkach nawigację i planowanie tras w przestrzeni miejskiej. Zamiast upraszczać dostępność do binarnej etykiety („dostępne/niedostępne”), dostarcza szczegółowych informacji o konkretnych barierach (schody, nachylenie, nawierzchnia, krawężniki) oraz wiarygodności i pochodzeniu danych. Pozwala reagować na żywo na przeszkody poprzez crowdsourcingowe zgłoszenia i automatyczne wyznaczanie objazdu.

## Positioning

1. **Konkretne fizyczne bariery zamiast ocen ogólnych**: Prezentacja dokładnych cech trasy (nachylenie, typ i stan nawierzchni, schody, krawężniki, szerokość przejścia) zamiast uproszczonego statusu.
2. **Przezroczysta proweniencja i pewność danych**: Jawne oznaczanie źródeł (OSM, otwarte dane miejskie, zgłoszenia użytkowników), dat aktualizacji i statusów wiarygodności (*Zweryfikowane*, *Do potwierdzenia*, *Nieznane*, *Demonstracyjne*).
3. **Nieznane ≠ Dostępne**: Brak danych traktowany jest jako niepewność i domyślnie omijany przez algorytm routingu.

## Operating Context

- **Planowanie przed wyjazdem**: Przeglądanie mapy Krakowa z warstwami barier/POI oraz tekstowej listy odcinków trasy.
- **Dopasowanie parametrów trasy**: Ustawianie akceptowalnego nachylenia (domyślnie 6%), tolerancji barier (schody, rampy, windy) i nawierzchni.
- **Nawigacja i reagowanie w trakcie jazdy**: Symulowany/rzeczywisty podgląd trasy z możliwością natychmiastowego zgłoszenia barier z aktualnej pozycji i przeliczenia objazdu.

## Capabilities and Constraints

- **Modułowy Monolit (Django + Frontend Web)**: Czyste rozdzielenie logiki (usunięte bezpośrednie mutacje DB z widoków na rzecz `services.py` / `selectors.py`).
- **Pipeline danych przestrzennych**: Przetwarzanie wycinków OSM (`.osm.pbf`) oraz danych wysokościowych DEM/SRTM w lokalny graf 3D bez nadmiernego odpytywania zewnętrznych API.
- **Zakres demonstracyjny**: Centrum Krakowa, przygotowana trasa demonstracyjna z jasnym oznaczeniem fikcyjnych i rzeczywistych barier.

## Brand Commitments

- **Nazwa**: Przejezdni
- **Tożsamość**: Niezależność, wiarygodność danych, społecznościowa współpraca, pełna dostępność cyfrowa.
- **Język interfejsu**: Polski (z architekturą pod i18n).

## Evidence on Hand

- `REQUIREMENTS.md` – Wymagania konkursowe i kryteria dostępności (WCAG 2.2 AA).
- `docs/product.md` – Specyfikacja produktu i zakresu demonstracji.
- `docs/routing.md` – Analiza logiki routingu i parametrów.
- Datasets: `krakow-bbox-*.osm.pbf`, `city_network_3d.graphml`, `accessibility_details.geojson`.

## Product Principles

1. **Szczegóły zamiast uproszczeń** – Prezentujemy konkretne przeszkody i parametry fizyczne zamiast etykiet binarnej dostępności.
2. **Nieznane nie oznacza dostępne** – Brak informacji to niepewność i domyślne ryzyko omijane w routingu.
3. **Użytkownik decyduje** – Parametry routingu dostosowywane są do indywidualnych możliwości i akceptacji ryzyka przez użytkownika.
4. **Dane mają pochodzenie** – Wszystkie cechy i punkty zawierają źródło, datę oraz wskaźnik zaufania.
5. **Dostępność cyfrowa jest fundamentem** – Interfejs spełnia WCAG 2.2 AA, oferując pełną obsługę klawiatury, czytników ekranu i alternatywy tekstowe dla mapy.

## Accessibility & Inclusion

- Pełna zgodność z **WCAG 2.2 AA**.
- Obsługa klawiatury z wyraźnym fokusem.
- Czytelne etykiety semantyczne i alternatywy tekstowe dla całej zawartości mapy.
- Bezpieczny kontrast oraz przekazywanie stanów i statusów zaufania bez polegania wyłącznie na kolorach.
