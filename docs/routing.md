# Analiza routingu dla Przejezdni

## Decyzja

Na potrzeby pierwszej demonstracji wybieramy **jedną przygotowaną trasę od
punktu A do punktu B**. Nie będzie to przypadkowo narysowana linia, ale trasa
wyliczona wcześniej na podstawie lokalnych danych OSM i zapisana jako mały
fixture demonstracyjny.

Jest to zgodne z dokumentem produktu (`docs/product.md`): w obecnej
demonstracji routing dynamiczny dowolnych tras jest poza zakresem, a trasa
przygotowana, kontrolowane scenariusze oraz mockowane zachowanie są dozwolone.
Demo ma pokazać docelowe doświadczenie produktu, a nie udawać gotowego systemu
nawigacyjnego.

Na etapie researchu i prac koncepcyjnych powstał już działający mechanizm
wyboru punktów oraz wyznaczania trasy na lokalnym grafie z użyciem algorytmu
Dijkstry. Kolejnym etapem nie jest więc implementacja algorytmu od zera, ale
integracja tego mechanizmu z produktem: parametrami użytkownika, polityką
brakujących danych, proweniencją, wyjaśnieniami trasy, wdrożeniem grafu i
testami.

## Kontekst produktu

Przejezdni pomaga osobom poruszającym się na wózkach zmniejszyć
nieprzewidywalność przejazdu. Routing nie może ograniczać się do wartości
„dostępna” albo „niedostępna”. Powinien pokazywać konkretne cechy odcinków:

- nawierzchnię i jej gładkość;
- nachylenie;
- schody, rampy i windy;
- krawężniki, przejścia i oznaczenia dotykowe, jeżeli są dostępne;
- szerokość przejścia, jeżeli jest znana;
- źródło, datę i status wiarygodności każdej istotnej informacji.

Docelowy przepływ produktu jest następujący:

1. Użytkownik wybiera początek i cel podróży.
2. Ustawia parametry zgodnie ze swoimi możliwościami i sytuacją.
3. Otrzymuje trasę wraz z listą znanych barier i ułatwień.
4. W trakcie przejazdu zgłasza napotkaną przeszkodę.
5. System pokazuje objazd.
6. Zgłoszenie może wzbogacić informacje dla kolejnych użytkowników.

W wersji demonstracyjnej punkty, trasa, zgłoszenie i objazd mogą być
kontrolowane. Muszą być jednak jawnie oznaczone jako demonstracyjne, jeżeli
nie są faktem odczytanym z danych mapowych.

## Dane dostępne obecnie

Dane lokalne zostały sprawdzone 2026-10-03. To przykładowy snapshot obejmujący
wycinek centrum Krakowa przygotowany na potrzeby demonstracji, a nie kompletne
ani produkcyjne dane miasta.

| Artefakt | Stan | Znaczenie dla routingu |
| --- | --- | --- |
| `city_network_3d.graphml` | 11 655 węzłów, 26 082 skierowane krawędzie, około 46 MB | Główny graf routingu; zawiera współrzędne, wysokość, długość krawędzi, nachylenie, nawierzchnię i koszty dostępności |
| `roads_3d.geojson` | 26 082 obiekty `LineString`, około 12 MB | Ta sama sieć do wyświetlania na mapie; zawiera geometrię, `u`, `v`, długość, nachylenie, nawierzchnię i koszty |
| `malopolskie-latest.osm.pbf` | Około 193 MB | Lokalne źródło OSM wykorzystywane przez pipeline; nie powinno być ładowane w żądaniu webowym |
| `generate_static_data.py` | Istniejący pipeline offline | Buduje sieć pieszą, pobiera szczegóły dostępności, dodaje wysokość, oblicza kary i eksportuje graf oraz GeoJSON |
| `accessibility_details.geojson` | 3 obiekty w obecnym trybie fast | Warstwa szczegółów barier; obecnie zbyt mała, aby samodzielnie obsłużyć routing |
| `accessible_pois.geojson` | 312 obiektów | Może dostarczać miejsca startu i celu, ale trasa demonstracyjna nie powinna zależeć od kompletności POI |

Obecny graf obejmuje centrum Krakowa w przybliżeniu:

- długość geograficzna: `19.9279412`–`19.9511314`;
- szerokość geograficzna: `50.049333`–`50.0707624`.

Generator działa obecnie w `FAST_MODE` i używa obszaru
`[19.93, 50.05, 19.95, 50.07]`. Jest to dobry zakres do powtarzalnego demo,
ale nie pełny graf Krakowa.

## Jakość danych i konsekwencje

Graf jest wystarczający do pokazania idei, ale nie powinien być jeszcze
prezentowany jako gwarancja bezpiecznej nawigacji:

- 22 862 krawędzie mają znaną nawierzchnię, a 3 220 nie ma wartości `surface`;
- tylko 110 krawędzi ma jawny tag `wheelchair` (`yes`, `no`, `designated` lub
  `limited`), a 25 972 nie ma takiej wartości;
- 646 krawędzi ma `highway=steps`;
- 626 krawędzi ma karę dostępności co najmniej `100`;
- 2 072 krawędzie mają nachylenie powyżej 6%;
- obecne wartości wysokości zawierają skrajne nachylenia, do około 1 340%, co
  wymaga walidacji przed użyciem jako twardego ograniczenia.

Najważniejsza zasada produktu brzmi: **brak danych nie oznacza dostępności**.
W routingu należy wykluczać odcinki bez wystarczających danych do oceny
wybranych parametrów. Nie oznacza to konieczności posiadania wartości dla
każdego możliwego tagu, ale dla każdej decyzji trasy trzeba znać wymagane
cechy, na przykład nawierzchnię, nachylenie i obecność schodów.

Jeżeli po zastosowaniu wymagań nie ma trasy, interfejs powinien pokazać brak
wyniku oraz wyjaśnić, czy powodem są ograniczenia danych, czy parametry
użytkownika. Nie wolno zwracać dowolnej trasy tylko po to, aby wynik istniał.

## Parametry routingu Przejezdni

Początkowe wartości wynikają z `docs/product.md` i są hipotezą do późniejszej
walidacji z użytkownikami. Nie opisują medycznych możliwości osoby.

| Parametr | Domyślna reguła demonstracyjna |
| --- | --- |
| Maksymalne nachylenie | 6% |
| Schody | Nie akceptuj |
| Rampy | Akceptuj |
| Windy | Akceptuj |
| Ruchome schody | Nie akceptuj |
| Gładkie przejście dla pieszych | Preferuj lub wymagaj zależnie od trybu |
| Wąski chodnik | Nie akceptuj |
| Asfalt | Akceptuj |
| Gładka kostka / płyty (`paving_stones`, `sett` + `smoothness=good/excellent`) | Akceptuj |
| Nierówny bruk / kocie łby | Nie akceptuj |
| Piasek, żwir i miękkie podłoże | Nie akceptuj |
| Nieznana lub niejednoznaczna nawierzchnia | Nie akceptuj domyślnie; osobny opt-in |

W demo parametry muszą mieć widoczny wpływ na opis trasy. Jeżeli interfejs
pokazuje zmianę ustawienia, powinien pokazać również, które odcinki zostały
zaakceptowane, odrzucone albo oznaczone jako nieznane.

Każda nawierzchnia bez wartości `smoothness` jest traktowana jako nieznana,
a nie jako dostępna. Użytkownik może jawnie włączyć parametr
`allow_unknown_surfaces`, ale wynik musi wtedy pokazać ostrzeżenie o odcinkach
bez potwierdzonego stanu nawierzchni.

## Weryfikacja kandydata A/B

W ramach osobnej analizy danych sprawdziliśmy przykładową parę punktów w
rejonie Rynku Głównego i Galerii Krakowskiej. Dla tej pary graf pozwolił
wyznaczyć trasę o długości około 1 206 m przy wadze `accessibility_cost`.
Trasa ta nie spełnia jednak domyślnego, ścisłego profilu produktu: po
wykluczeniu nieznanych nawierzchni, nachylenia powyżej 6% i schodów dla tych
konkretnych punktów nie znaleziono ścieżki.

Podane poniżej współrzędne nie są stałymi punktami produktu. Istniejący
mechanizm pozwala wybrać dowolny punkt A i B, a te współrzędne służą wyłącznie
do analizy przykładowego fragmentu danych i nie powinny być traktowane jako
gotowa trasa demonstracyjna.

To nie jest powód, aby wrócić do przypadkowej polilinii. Przed zapisaniem
fixture'a należy wybrać punkty A/B, dla których da się przygotować trasę
zgodną z jawną polityką danych. Proces wyboru powinien:

1. przyciągnąć punkty do najbliższych węzłów grafu;
2. odrzucić krawędzie z nachyleniem powyżej 6%, `highway=steps` oraz
   nieakceptowaną lub nieznaną nawierzchnią;
3. wyznaczyć trasę po pozostałym grafie;
4. ręcznie sprawdzić przebieg na mapie;
5. zapisać dokładne punkty, reguły i wynik w fixture'ze.

Po zastosowaniu opisanych reguł, w analizowanym fragmencie obecny graf ma
trasę około 667 m i 41 węzłów między przykładowymi punktami:

- A: `50.061744, 19.934232`;
- B: `50.065275, 19.935753`.

Jest to wynik analizy bieżącego grafu, a nie wynik wyboru stałych punktów przez
produkt. Mechanizm routingu obsługuje wybór dowolnych punktów; na potrzeby demo
możemy jednak zapisać jeden wybrany scenariusz jako powtarzalny fixture.
Przed zapisaniem fixture'a trzeba zweryfikować jego przebieg, proweniencję i
zgodność z parametrami użytkownika.

## Porównanie sposobów realizacji

### 1. Przygotowana trasa demonstracyjna

Trasa jest wyliczana offline i zapisywana jako mały fixture zawierający
przebieg, odcinki, parametry oraz proweniencję.

**Zalety:**

- najszybsza droga do działającej animacji;
- identyczny wynik przy każdym pokazie;
- brak zależności od sieci, zewnętrznego API i limitów zapytań;
- brak parsowania GraphML lub PBF w żądaniu Django;
- możliwość ręcznego sprawdzenia trasy przed prezentacją;
- łatwe pokazanie pełnego scenariusza: trasa, przeszkoda, zgłoszenie i objazd.

**Ograniczenia:**

- obsługuje przygotowane punkty, a nie dowolny wybór użytkownika;
- zmiana parametrów może być kontrolowanym scenariuszem, a nie ponownym
  przeliczeniem dowolnej trasy;
- fixture wygenerowany z lokalnych, ignorowanych plików musi zawierać własną
  proweniencję i mieć powtarzalny sposób odtworzenia.

### 2. Dynamiczny routing na lokalnym grafie

Backend ładuje graf, przyciąga dowolne współrzędne do węzłów i uruchamia
Dijkstrę albo A* z parametrami użytkownika.

**Zalety:**

- realizuje docelową funkcję produktu;
- umożliwia indywidualne ustawienia i ponowne wyznaczenie trasy;
- pozwala pokazać, dlaczego trasa jest dłuższa i jakie bariery omija;
- nie wymaga zewnętrznego serwisu routingowego.

**Dodatkowa praca:**

- osobny serwis routingu i selektory, zamiast logiki w widoku;
- ładowanie i cache grafu;
- przyciąganie współrzędnych oraz obsługa rozłącznych fragmentów;
- formalna polityka brakujących danych;
- filtry nachylenia, schodów, ramp, wind, nawierzchni i szerokości;
- lista tekstowa odcinków, barier i ułatwień;
- testy usług, API i przypadków brzegowych;
- dostarczenie grafu w środowisku wdrożeniowym;
- proweniencja i status wiarygodności w odpowiedzi API.

Mechanizm obliczeniowy już istnieje, ale jego pełna integracja z produktem
jest większa niż zakres samej animacji demonstracyjnej. Dlatego najszybszym
wariantem demo pozostaje zapisanie jego wyniku jako kontrolowanego fixture'a.

### 3. Zewnętrzne API routingowe

OSRM lub podobny serwis może szybko zwrócić trasę, ale standardowa trasa
piesza nie będzie wiarygodnie stosować parametrów Przejezdni dla wózków,
takich jak maksymalne nachylenie, schody, nieznane dane i konkretne
nawierzchnie.

Dochodzi zależność od dostępności sieci, limitów, prywatności,
powtarzalności wyników i działania usługi podczas prezentacji. To rozwiązanie
nie jest rekomendowane dla pierwszej wersji.

## Rekomendowany fixture demonstracyjny

Fixture powinien być mały i niezależny od 46 MB GraphML w czasie działania
aplikacji. Powinien zawierać co najmniej:

- `route_id`;
- oznaczenie `demonstracyjne`;
- punkty A i B oraz punkty przyciągnięte do grafu;
- uporządkowaną geometrię trasy;
- dystans i parametry użyte przy wyborze;
- odcinki z nawierzchnią, nachyleniem, barierami i ułatwieniami;
- status każdej istotnej informacji;
- źródło danych, datę snapshotu i identyfikator generatora;
- informację, które elementy są rzeczywiste z OSM, a które są mockowane.

Fixture powinien mieć co najmniej dwa kontrolowane stany:

1. `initial` – przygotowana trasa z listą znanych informacji;
2. `after_report` – objazd po zgłoszeniu bariery.

Jeżeli przeszkoda w drugim stanie jest fikcyjna, musi mieć status
**Demonstracyjne** i nie może być prezentowana jako aktualny fakt. Jeżeli
pochodzi z OSM, interfejs powinien pokazać źródło i datę snapshotu.

Nie należy zapisywać samej polilinii bez kontekstu. Model trasy musi umożliwić
wyświetlenie informacji zarówno na mapie, jak i w tekstowej liście.

## Przebieg demonstracji

Minimalny scenariusz powinien pokazać:

1. wybór lub wskazanie przygotowanych punktów A i B;
2. ustawienie parametrów, w tym domyślnego limitu nachylenia 6%;
3. animowane tworzenie trasy na mapie;
4. listę odcinków z nawierzchnią, nachyleniem, barierami i statusami danych;
5. symulowane przejście po kolejnych odcinkach;
6. pojawienie się znanej albo jawnie fikcyjnej przeszkody;
7. akcję „Zgłoś utrudnienie”;
8. status zgłoszenia „Do potwierdzenia”;
9. pokazanie przygotowanego objazdu;
10. informację, że zgłoszenie może być użyte przez innych użytkowników.

Zmiana parametrów w demonstracji może przełączać przygotowane warianty, ale
interfejs nie może sugerować, że uruchomiono pełny routing dynamiczny, jeżeli
wynik pochodzi z fixture'a.

## Statusy i proweniencja danych

Każdy element wpływający na ocenę trasy powinien mieć jeden z produktowych
statusów:

| Status | Znaczenie w routingu |
| --- | --- |
| Zweryfikowane | Informacja potwierdzona zgodnie z przyjętym procesem |
| Do potwierdzenia | Zgłoszenie lub inne źródło, którego jeszcze nie potwierdzono |
| Nieznane / brak danych | Za mało informacji, aby ocenić odcinek |
| Demonstracyjne | Dane przygotowane albo fikcyjne wyłącznie na potrzeby prezentacji |

Status „Do potwierdzenia” nie może wyglądać jak „Zweryfikowane”. Status
„Nieznane / brak danych” nie jest dowodem dostępności. W panelu szczegółów
trasy powinny być widoczne:

- źródło, na przykład OSM albo zgłoszenie użytkownika;
- data pozyskania lub ostatniej weryfikacji;
- status wiarygodności;
- identyfikator snapshotu lub zgłoszenia, jeżeli istnieje.

## Dostępność interfejsu

Animacja nie może być jedynym sposobem zrozumienia trasy. Zgodnie z
założeniami produktu interfejs powinien zapewniać:

- tekstową listę odcinków i barier;
- semantyczne przyciski do rozpoczęcia, zatrzymania, wznowienia, pominięcia i
  powtórzenia animacji;
- widoczny fokus i pełną obsługę klawiaturą;
- komunikaty o zmianie trasy i zgłoszeniu dla czytników ekranu;
- informacje niezależne od samego koloru;
- jasne rozróżnienie danych zweryfikowanych, niezweryfikowanych, nieznanych i
  demonstracyjnych.

## Architektura i kolejność prac

### Etap 1: demo

1. Wybrać i ręcznie zatwierdzić punkty A/B zgodne z polityką danych.
2. Uruchomić istniejący mechanizm Dijkstry i wygenerować fixture offline z
   istniejącego grafu.
3. Dodać metadane źródła, daty, statusów i wariantów scenariusza.
4. Udostępnić stabilny model trasy dla frontendu.
5. Dodać warstwę trasy, animację, listę tekstową i panel szczegółów.
6. Dodać kontrolowany scenariusz bariery, zgłoszenia i objazdu.

Fixture nie powinien wymagać GraphML ani PBF w czasie działania. Pliki
`*.graphml` i `*.geojson` są ignorowane przez `.gitignore`, dlatego sama
obecność lokalnego pliku nie może być założeniem wdrożenia. Sposób generowania
fixture'a powinien być opisany w pipeline i zapisywać snapshot źródłowych
danych.

### Etap 2: integracja działającego prototypu routingu

1. Wydzielić istniejący mechanizm do serwisu odpowiedzialnego za ładowanie
   grafu i wyznaczanie trasy.
2. Dodać selektor najbliższego węzła jako stabilny element API mechanizmu.
3. Podłączyć Dijkstrę do parametrów użytkownika i polityki brakujących danych.
4. Zwracać ten sam model odcinka, który wykorzystuje fixture demonstracyjny.
5. Dodawać alternatywne trasy i wyjaśnienie decyzji algorytmu.
6. Zasilać trasę zgłoszeniami barier ze statusem „Do potwierdzenia”.
7. Rozszerzyć obszar poza `FAST_MODE` po walidacji danych wysokościowych.

## Rekomendacja końcowa

Na obecnym etapie wybieramy **przygotowaną trasę demonstracyjną opartą na
lokalnych danych OSM**, z jawnie opisanymi parametrami, źródłami i statusami.
Nie wybieramy losowej polilinii ani zewnętrznego API.

To rozwiązanie najlepiej odpowiada zakresowi hackathonowej demonstracji
Przejezdni: pozwala pokazać trasę, bariery, zgłoszenie i objazd w sposób
powtarzalny, bez składania obietnicy dynamicznej nawigacji. Dynamiczny routing
na lokalnym grafie należy wdrożyć jako kolejny etap integracji, zachowując ten
sam model trasy i wykorzystując fixture demonstracyjny jako test regresyjny
dla istniejącego mechanizmu Dijkstry.
