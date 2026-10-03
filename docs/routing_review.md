# Przegląd implementacji routingu

## Cel przeglądu

Dokument zbiera wyniki walidacji aktualnej implementacji wyznaczania trasy w
kontekście:

- `REQUIREMENTS.md`;
- `docs/product.md`;
- `docs/routing.md`;
- aktualnego przykładowego snapshotu danych centrum Krakowa.

Przegląd obejmował:

- `hackyeah2026/map/selectors.py`;
- `hackyeah2026/map/services.py`;
- `hackyeah2026/map/views.py`;
- `hackyeah2026/map/urls.py`;
- `hackyeah2026/map/templates/map/route.html`;
- `generate_static_data.py`;
- testy routingu w `hackyeah2026/map/tests/`;
- `data_provenance.json`.

## Wniosek ogólny

Mechanizm techniczny działa: punkty A i B można wybrać, graf jest ładowany i
cache'owany, a algorytm Dijkstry zwraca GeoJSON, podsumowanie i listę odcinków.
Nie jest jednak jeszcze zgodny z zasadami Przejezdni dotyczącymi parametrów
użytkownika, brakujących danych, proweniencji i statusów wiarygodności.

Najpoważniejszy problem polega na tym, że system może zwrócić trasę łamiącą
ustawienia użytkownika, a następnie pokazać ją bez jednoznacznego ostrzeżenia.
Drugi krytyczny problem to traktowanie części brakujących danych jak braku
przeszkody.

## Co działa zgodnie z założeniami

- Logika odczytu grafu znajduje się w `selectors.py`, a logika routingu w
  `services.py`, zamiast w widoku.
- Punkty A i B mogą być wskazane na mapie lub wpisane ręcznie.
- Graf jest ładowany tylko raz na proces dzięki cache'owi.
- API zwraca geometrię GeoJSON, dystans, statystyki oraz instrukcje tekstowe.
- Dostępne są podstawowe ustawienia nachylenia, schodów, ramp, wind,
  nawierzchni i szerokości.
- Wykluczenie odcinka powoduje ponowne wyznaczenie trasy.
- Istnieje podstawowa tekstowa lista odcinków oraz karta źródła danych.

To jest dobry fundament prototypu. Poniższe problemy wymagają jednak
rozwiązania przed przedstawianiem wyniku jako trasy zgodnej z preferencjami
użytkownika.

## Wyniki testów

Lokalnie wykonano:

```text
uv run pytest -q
15 passed

make quality-check
ruff format: passed
ruff check: passed
dmypy: passed
```

Testy przechodzą w obecnym workspace, ponieważ znajdują się w nim ignorowane
pliki z grafem. Nie oznacza to jeszcze, że routing przejdzie w czystym
checkoutcie CI lub na wdrożeniu.

## Znalezione niezgodności

### 1. Krytyczne: automatyczne rozluźnianie ograniczeń użytkownika

**Miejsce:** `hackyeah2026/map/services.py:228-247`

Jeżeli trasa nie zostanie znaleziona, `_find_path()` wykonuje drugą próbę z
następującymi zmianami:

- włącza schody;
- wyłącza unikanie bruku;
- podnosi maksymalne nachylenie do co najmniej 12%;
- czyści `excluded_barriers`.

Jest to sprzeczne z `docs/product.md` oraz `docs/routing.md`. Jeżeli nie ma
trasy spełniającej parametry, system powinien zakomunikować brak trasy i
wyjaśnić przyczynę, a nie zwracać trasę łamiącą ustawienia.

Backend zwraca pole `is_relaxed`, ale frontend go nie pokazuje
(`route.html:963-965`, `994-1033`). Użytkownik nie wie więc, że otrzymał
wynik awaryjny.

**Konsekwencja:** użytkownik może ustawić zakaz schodów lub maksymalnie 6%, a
otrzymać trasę z tymi barierami.

**Zalecenie:** usunąć ciche rozluźnianie. Jeżeli ma pozostać tryb awaryjny,
powinien być uruchamiany jawnie przez użytkownika i zwracać wyraźny status
„trasa poza ustawieniami”.

### 2. Krytyczne: brak danych może zostać potraktowany jako dostępność

**Miejsce:** `hackyeah2026/map/services.py:165-186`, `128-139`, `437-442`

Nieznana nawierzchnia jest zamieniana na tekst, który nie należy do zbioru
trudnych nawierzchni, i otrzymuje normalny koszt. Nieznana szerokość również
nie blokuje odcinka. Podsumowanie uwzględnia tylko wybrane bariery:

- schody;
- nachylenie;
- trudną nawierzchnię;
- wysokie krawężniki.

Nie uwzględnia braku danych o nawierzchni, szerokości, gładkości, przejściu,
rampie ani windzie. W efekcie trasa może otrzymać status „Pełna dostępność”,
mimo że nie wszystkie wymagane informacje są znane.

To narusza zasadę „nieznane nie oznacza dostępne” oraz
`REQUIREMENTS.md` dotyczącą brakujących danych.

**Zalecenie:** zdefiniować minimalny zestaw danych wymagany do oceny odcinka.
Odcinek niespełniający tego zestawu powinien być wykluczony w trybie
domyślnym albo oznaczony jako nieznany i nie może podnosić statusu dostępności.

### 3. Wysokie: nawierzchnie odrzucane przez produkt nie są faktycznie blokowane

**Miejsce:** `hackyeah2026/map/services.py:101-125`

Przy `avoid_cobblestone=True` bruk, żwir i podobne nawierzchnie otrzymują
karę, ale nadal mogą należeć do zwróconej trasy. Dokument produktu określa
piasek, żwir oraz bruk/kocie łby jako nawierzchnie domyślnie nieakceptowane,
nie tylko mniej preferowane.

W reprodukcji dla przykładowych punktów A/B domyślna trasa zawierała 17
odcinków sklasyfikowanych jako bruk/trudna nawierzchnia.

**Zalecenie:** rozdzielić tryb „wyklucz” od trybu „preferuj”. Domyślne
ustawienia z dokumentu produktu powinny wykluczać wskazane nawierzchnie.

### 4. Wysokie: część kontrolek UI nie wpływa na wynik routingu

**Miejsca:** `views.py:95-112`, `services.py:142-193`

`smooth_crossing` jest odczytywane z API, ale nie jest używane w funkcji wagi.
Włączenie i wyłączenie tej opcji daje ten sam wynik.

`allow_ramps` i `allow_elevators` wpływają wyłącznie na obsługę schodów z
odpowiednim udogodnieniem. Nie powodują preferowania ramp ani wind na zwykłej
trasie. Brak danych o tych elementach nie jest rozróżniany od ich braku.

`avoid_narrow` domyślnie ma wartość `False`, mimo że dokument produktu opisuje
wąski chodnik jako domyślnie nieakceptowany. Przy braku wartości `width`
odcinek nadal przechodzi.

**Zalecenie:** każda kontrolka powinna mieć jednoznacznie zdefiniowany wpływ
na koszt albo dostępność krawędzi i test sprawdzający zmianę wyniku.

### 5. Wysokie: obsługa schodów, ramp i wind jest blokowana przez filtr nachylenia

**Miejsca:** `generate_static_data.py:441-445`, `services.py:175-183`

Generator przypisuje schodom `grade_abs=0.25`, czyli 25%. Następnie filtr
nachylenia odrzuca je przy maksymalnym nachyleniu 6%, nawet jeśli użytkownik
zezwolił na schody albo schody mają rampę lub windę.

W praktyce opcje „Zezwól na schody”, „Preferuj rampy” i „Korzystaj z wind”
nie mogą zadziałać zgodnie z opisem przy zakresie suwaka do 15%.

**Zalecenie:** najpierw oceniać typ bariery i dostępne udogodnienie, a dopiero
potem stosować limit nachylenia do odcinków, dla których ten limit ma sens.
Należy też upewnić się, że atrybuty `elevator` i `ramp:wheelchair` są obecne
w grafie routingu, a nie tylko w warstwie szczegółów.

### 6. Wysokie: proweniencja jest niepełna i zawiera zbyt mocny status

**Miejsca:** `services.py:473-479`, `route.html:1027-1033`

API wpisuje na stałe:

```text
Zweryfikowano numerycznie (DEM + OSM tags)
```

Obliczenie trasy na podstawie OSM i DEM nie oznacza fizycznej weryfikacji
dostępności. Aktualne dane są przykładowym snapshotem wycinka centrum Krakowa.
Brak również statusu osobno dla każdego istotnego elementu odcinka.

`data_provenance.json` opisuje inny stan danych niż aktualny graf:

- provenance: 4 182 węzły i 11 136 krawędzi;
- aktualny graf lokalny: 11 655 węzłów i 26 082 krawędzie;
- provenance wskazuje plik `malopolskie-261002.osm.pbf`, podczas gdy obecny
  pipeline używa `malopolskie-latest.osm.pbf`.

Frontend pokazuje źródło i datę tylko w zbiorczej karcie trasy. Instrukcje nie
mają własnego źródła, daty ani statusu wiarygodności.

**Zalecenie:** API powinno czytać wersjonowane metadane pipeline'u, pokazywać
rzeczywisty snapshot oraz stosować status „Nieznane / brak danych” albo „Do
potwierdzenia”, gdy nie ma procesu weryfikacji terenowej.

### 7. Wysokie: brak kontroli zakresu współrzędnych i odległości przyciągnięcia

**Miejsce:** `hackyeah2026/map/selectors.py:63-69`

`find_nearest_node()` zwraca odległość do najbliższego węzła, ale routing jej
nie sprawdza. Dowolne współrzędne są przyciągane do grafu centrum Krakowa.

Podczas testu współrzędne Warszawy oraz `[0, 0]` również zwróciły trasę po
krakowskim grafie. Współrzędne spoza obszaru demonstracyjnego nie powinny być
prezentowane jako poprawnie obsłużony punkt.

**Zalecenie:** dodać walidację zakresu geograficznego, maksymalną odległość
przyciągnięcia oraz zwracanie błędu wyjaśniającego, że punkt znajduje się poza
obszarem danych.

### 8. Wysokie: zwracane metadane mogą nie odpowiadać krawędzi wybranej przez algorytm

**Miejsce:** `hackyeah2026/map/services.py:196-225`

Graf jest `MultiDiGraph`, ale po wyznaczeniu listy węzłów kod wybiera krawędź
o najmniejszej długości, a nie krawędź wybraną przez funkcję kosztu Dijkstry.
W aktualnym grafie istnieją równoległe krawędzie.

Dodatkowo:

- `edge_ids` nie zawierają klucza krawędzi multigrafu;
- wykluczenie pary węzłów może wykluczyć więcej krawędzi niż zamierzono;
- geometria odpowiedzi jest zbudowana z punktów węzłów, a nie z geometrii
  krawędzi.

W rezultacie opis nawierzchni, ostrzeżenia i wykluczenie odcinka mogą dotyczyć
innej krawędzi niż ta, która wpłynęła na wynik Dijkstry.

**Zalecenie:** używać klucza krawędzi w ścieżce, zachować wybraną krawędź w
wyniku algorytmu i zwracać jej rzeczywistą geometrię.

### 9. Wysokie: aktualny kod nie realizuje jeszcze kontraktu demo z `routing.md`

Dokument routingu definiuje przygotowany fixture oraz kontrolowany scenariusz:

```text
initial → przeszkoda → zgłoszenie → after_report
```

Aktualny frontend (`route.html:913-971`) wywołuje dynamiczne API dla dowolnych
punktów i rysuje całą linię od razu. Brakuje:

- fixture'a z `route_id` i snapshotem;
- stanów `initial` i `after_report`;
- animacji tworzenia trasy;
- przycisków zatrzymania, wznowienia, pominięcia i powtórzenia;
- zgłoszenia bariery z kategorią, opisem i lokalizacją;
- statusu zgłoszenia „Do potwierdzenia”;
- przygotowanego objazdu po zgłoszeniu.

Funkcja `excludeEdges()` jest lokalnym wykluczeniem odcinka i ponownym
przeliczeniem, ale nie zastępuje przepływu zgłoszenia bariery opisanego w
dokumencie produktu.

### 10. Wysokie: testy nie są niezależne od lokalnych artefaktów danych

`city_network_3d.graphml` i pliki GeoJSON są ignorowane przez `.gitignore` i
nie są śledzone w repozytorium. Testy routingu bez tych plików nie mają
zastępczego, małego grafu testowego.

W czystym checkoutcie CI testy wywołujące `get_routing_graph()` zakończą się
brakiem pliku, chyba że pipeline generowania danych zostanie uruchomiony przed
testami. Sam `data_provenance.json` nie dostarcza grafu.

**Zalecenie:** testy serwisu powinny używać małego grafu tworzonego w fixture,
a osobny test integracyjny powinien jawnie wymagać wygenerowanych danych.

### 11. Średnie: interfejs nie spełnia jeszcze wymagań dostępności dla listy trasy

**Miejsce:** `route.html:1119-1155`

Elementy kroków trasy są klikalnymi `<div>` zamiast semantycznymi przyciskami
lub elementami z pełną obsługą klawiatury. Nie mają `tabindex`, obsługi Enter/Spacji
ani odpowiednich nazw dla czytnika ekranu.

Brakuje również `aria-live` dla:

- wyniku wyznaczania trasy;
- błędu API;
- zmiany trasy;
- przyjęcia zgłoszenia.

Mapa ma tekstową listę, co jest dobrym kierunkiem, ale interakcja z listą nie
jest jeszcze dostępna z klawiatury.

### 12. Średnie: brak mechanizmu korekty lub zgłoszenia danych

Wymagania produktu przewidują możliwość zgłoszenia i korekty nieaktualnych
danych. Aktualna funkcja wykluczenia odcinka działa tylko dla bieżącego
zapytania i nie zapisuje zgłoszenia, jego kategorii, opisu ani statusu
„Do potwierdzenia”.

To oznacza, że istnieje mechanizm eksperymentowania z trasą, ale nie istnieje
jeszcze produktowy przepływ zgłoszenia bariery.

### 13. Niskie/średnie: ryzyka techniczne w API i frontendzie

- `route_api` jest oznaczone `@csrf_exempt` (`views.py:46`), mimo że obsługuje
  żądania POST.
- API zwraca szczegóły wyjątków w odpowiedzi 500 (`views.py:119-120`).
- Dane z OSM są wstawiane do `innerHTML` bez konsekwentnego escapowania w
  `route.html:1090-1101` i `1140-1149`. Nazwy obiektów lub inne tagi źródłowe
  mogą być niezaufanym wejściem.
- Test `test_services.py:48-50` utrwala status „Zweryfikowano numerycznie”,
  zamiast sprawdzać zgodność statusu z rzeczywistą proweniencją.

## Reprodukcje zachowania

Dla przykładowych punktów używanych w testach:

```text
start: 50.0617, 19.9373
end:   50.0645, 19.9413
```

Zaobserwowano:

- dystans około 685,6 m;
- maksymalne nachylenie 7,1% przy limicie 6% w teście API;
- 17 odcinków sklasyfikowanych jako bruk/trudna nawierzchnia;
- status `moderate`, mimo że domyślne ustawienia nie powinny akceptować
  części tych nawierzchni;
- zmiana `smooth_crossing` nie zmieniła wyniku;
- zmiana `avoid_narrow` nie zmieniła wyniku dla tego przypadku.

Dla współrzędnych spoza obszaru danych system zwrócił trasę po grafie Krakowa,
zamiast odrzucić żądanie.

## Priorytet napraw

### P0: bezpieczeństwo decyzji o trasie

1. Usunąć ciche rozluźnianie ograniczeń albo pokazywać je jako jawny tryb
   awaryjny.
2. Zablokować nieznane lub niewystarczająco opisane odcinki w trybie domyślnym.
3. Naprawić status dostępności, aby nie oznaczał brakujących danych jako pełnej
   dostępności.
4. Dodać kontrolę obszaru danych i maksymalnej odległości przyciągnięcia.
5. Zastąpić hardcoded provenance rzeczywistym snapshotem i statusami danych.

### P1: zgodność parametrów i poprawność wyniku

1. Zaimplementować faktyczny wpływ wszystkich kontrolek na routing.
2. Naprawić obsługę schodów, ramp i wind względem filtra nachylenia.
3. Zachować klucze wybranych krawędzi multigrafu i ich geometrię.
4. Dodać testy kontraktowe dla każdego parametru oraz przypadków braku trasy.

### P2: demo i jakość interfejsu

1. Dodać fixture `initial`/`after_report` oraz kontrolowany objazd.
2. Dodać animację z zatrzymaniem, wznowieniem, pominięciem i powtórzeniem.
3. Dodać produktowy przepływ zgłoszenia bariery.
4. Zastąpić klikalne `div` semantycznymi kontrolkami i dodać komunikaty
   `aria-live`.
5. Oddzielić testy małego grafu od testów wymagających danych demo.

## Ocena końcowa

Aktualna implementacja potwierdza, że techniczne wyznaczanie trasy między
dowolnymi punktami jest możliwe i działa na lokalnym grafie. Nie można jej
jednak jeszcze traktować jako zgodnej z modelem Przejezdni, ponieważ wynik nie
jest obecnie wystarczająco wiarygodny ani transparentny dla użytkownika.

Najpierw należy zagwarantować, że trasa nigdy nie łamie po cichu ustawień i
nie traktuje brakujących danych jako dostępności. Dopiero potem warto budować
na tym przygotowany fixture demonstracyjny i scenariusz zgłoszenia objazdu.
