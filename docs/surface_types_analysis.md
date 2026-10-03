# Analiza Nawierzchni (OSM Surface Tags) w Kontekście Dostępności

Dokument zawiera analizę wartości tagu `surface` (nawierzchnia) na podstawie danych OpenStreetMap dla województwa małopolskiego (plik `malopolskie-latest.osm.pbf`). 

## Czego dotyczą te powierzchnie?
W OpenStreetMap tag `surface` jest dodawany do tzw. dróg (ang. *ways*). W kontekście naszej aplikacji (siatka piesza / `network_type="walking"`) tag ten opisuje fizyczną nawierzchnię:
- **Chodników** (`highway=footway` lub `footway=sidewalk`)
- **Ścieżek w parkach i lasach** (`highway=path`)
- **Deptaków i rynków** (`highway=pedestrian`)
- **Przejść dla pieszych** (`highway=crossing`)
- **Współdzielonych dróg** (np. `highway=residential` bez wydzielonego chodnika)

Informacja o nawierzchni jest **krytyczna** dla wózków inwalidzkich, ponieważ decyduje o możliwości przejazdu, komforcie (wibracje) oraz bezpieczeństwie (ryzyko utknięcia małych przednich kółek).

---

## Wyniki ze skanowania woj. małopolskiego (Częstotliwość występowania)

Na podstawie szybkiego skanowania pliku PBF wydobyliśmy ponad 200 tysięcy przypisań tagu `surface`. Poniżej zostały one pogrupowane w kategorie pod kątem algorytmu wyznaczania bezpiecznych tras dla wózków (routingu).

### 🟢 Dobre i utwardzone (Niskie koszty w algorytmie)
Nawierzchnie gładkie, po których wózek inwalidzki porusza się bez oporów.
*   `asphalt` (asfalt) – **97 778**
*   `paving_stones` (równa kostka brukowa/płyty) – **73 234**
*   `paved` (ogólnie utwardzona) – **15 224**
*   `concrete` (beton) – **6 726**
*   `compacted` (ubita ziemia/szuter) – **3 224** (Zazwyczaj twarda, ale jej stan zależy od pogody)
*   `concrete:plates` (duże płyty betonowe) – **1 340**

### 🟡 Męczące i wyboiste (Zwiększone koszty / ostrzeżenia)
Nawierzchnie powodujące silne wibracje, duże opory toczenia, lub grząskie po opadach deszczu.
*   `ground` (goły grunt) – **17 582**
*   `unpaved` (nieutwardzona) – **10 521**
*   `gravel` (żwir) – **6 864**
*   `grass` (trawa) – **5 356**
*   `dirt` / `earth` (ziemia/klepisko) – **4 179**
*   `sett` (kamienna kostka brukowa - ciosana, wyboista) – **2 122**
*   `fine_gravel` (drobny żwir/szuter) – **2 079**
*   `grass_paver` (ażurowe płyty trawnikowe) – **699** (Bardzo trudne dla małych przednich kółek wózka)

### 🔴 Ekstremalne przeszkody (Trasy omijane przez algorytm)
Nawierzchnie stanowiące bezpośrednie zagrożenie utknięcia lub przewrócenia się wózka, albo powodujące ból użytkownika od ekstremalnych wibracji.
*   `pebblestone` (otoczaki / luźne kamienie) – **560**
*   `sand` (piasek - kółka natychmiast grzęzną) – **491**
*   `cobblestone` oraz `unhewn_cobblestone` (stary, mocno wypukły bruk - tzw. "kocie łby") – **329** (Często występuje w okolicach Starego Miasta)
*   `mud` (błoto) – **292**
*   `metal_grid` (metalowe kraty) – **85** (Istnieje wysokie ryzyko wpadnięcia przedniego kółka wózka i upadku)
*   `stepping_stones` (kamienie deptane/przez wodę) – **56**

## Wnioski dla implementacji Django
W module `services.py` przy wyznaczaniu wag w grafie (Dijkstra/A*), parametry te muszą posłużyć jako modyfikatory wagi:
- Mnożnik `1.0` dla nawierzchni z grupy zielonej.
- Mnożnik np. `2.0 - 4.0` dla grupy żółtej (omijaj jeśli to możliwe).
- Mnożnik `∞` (Infinity / zakaz wjazdu) dla grupy czerwonej (chyba że użytkownik zaznaczy w preferencjach asystę drugiej osoby).
