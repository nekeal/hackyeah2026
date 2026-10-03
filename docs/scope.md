# Scope projektu

Co jest ważne w projekcie:
- kod
- demo
- wideo
- link do repo/demo

## Źródła

- [x] OpenStreetMap (OSM)
- [x] SRTM DEM (dane wysokościowe / nachylenie)

## Kluczowe funkcjonalności

- [x] Mapa z punktami i trasą (UI z warstwami nawierzchni, 3D roads, POI oraz detalami dostępności)
- [ ] Wyznaczanie trasy między wybranymi punktami
- [ ] Lista punktów na trasie (wskazówki trasy)
- [x] Wyświetlanie ważnych punktów na mapie (od pewnego poziomu zbliżenia):
    - [x] schody, rampy, windy, ruchome schody
- [x] Informacje szczegółowe o punkcie (drawer / tooltip)
    - [x] przystosowanie do wózków (`wheelchair`, `wheelchair:description`)
    - [x] krawężniki (`kerb`)
    - [x] przejścia dla pieszych (`crossing`)
    - [x] oznaczenia dotykowe (`tactile_paving`)
    - [x] dodatkowe tagi (`toilets:wheelchair`, `elevator`, `ramp`, `lit`, `bench`, `shelter`, `level`)
- [ ] Możliwość wykluczenia danego typu punktów przez akcję na punkcie 
    - wybieram punkt -> wyklucz ten typ punktów z trasy -> poszukiwania nowej trasy
- [x] Filtrowanie po kątach nachylenia (analiza nachylenia z DEM/SRTM + `accessibility_penalty`)
- [ ] Nawigacja na trasie z użyciem GPS
- [ ] Możliwość dodawania własnych punktów do trasy

# Moduły

- [x] Mapa (Django view + Leaflet UI)
- [x] Punkty na mapie
    - [x] Ułatwienia dostępu / Utrudnienia (`accessibility_details.geojson` - kerb, crossing, tactile paving)
    - [x] Point of Interest (`accessible_pois.geojson` + filtry kategorialne + side drawer)
        - [x] Czy jest dostępny dla wózków?
        - [ ] (Opcjonalnie) Punkt niedostępny dla wózków -> wskazówka dla zarządcy obiektu
- [ ] Wyznaczanie trasy pomiędzy wybranymi punktami na mapie
- [ ] Lista nawigacyjna z ułatwieniami i utrudnieniami
- [ ] (Opcjonalne) Nawigacja na trasie z GPS
- [ ] Zgłaszanie utrudnień/ułatwień na trasie (aka Yanosik)

Note: OSRM - Open Source Routing Machine

Jakie ustawienia filtrowania? (obsługiwane w analizie i generatorze danych statycznych `generate_static_data.py`):
- [x] max nachylenie - default: 6% (wyznaczanie incline z SRTM)
- [x] schody - default: false (kary punktowe / wykrywanie schodów)
- [x] rampy - default: true (ekstrakcja tagu ramp w sieci i POI)
- [x] windy - default: true (ekstrakcja tagu elevator w sieci i POI)
- [x] ruchome schody - default: false
- [x] gładkie przejście dla pieszych - default: true (detekcja kerb, tactile_paving, crossing)
- [x] wąski chodnik - default: false (atrybuty width)
- [x] typ nawierzchni (przeanalizowane w `surface_types_analysis.md` i wdrożone w karach trasy):
    - [x] piasek: false
    - [x] żwir: false
    - [x] bruk / kocie łby: false
    - [x] asfalt: true
    - [x] ścieżka: true

# High concept
 
System map do wyszukiwania tras dla osób poruszających się na wózkach z wyspecjalizowanymi filtrami ułatwień i utrudnień. Oparte o dane z OpenStreetMaps i dodatkowe informacje crowdsourcingowe od użytkowników aplikacji.

# Co musimy zrobić do mocka

- [x] UI z mapą (`/map/` oraz `/map/pois/`)
- [ ] Ustawienie ogólnych filtrów (panel z opcjami)
- [ ] Wyszukiwanie trasy (lub dwóch)
- [ ] Wykluczenie utrudnienia (wszystkie schody) -> wyznaczenie nowej trasy
- [ ] Dodanie utrudnienia (wybrane jedne schody) -> wyznaczenie nowej trasy
- [ ] Nawigacja przez trasę
- [ ] Zgłoszenie utrudnienia -> wyznaczenie nowej trasy dla użytkownika z uwzględnieniem jego zgłoszenia (objazd)
- [x] Uwzględnić torowiska (`generate_static_data.py` - detekcja torowisk i przejść przez torowiska)

