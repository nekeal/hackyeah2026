# Przejezdni

## Dokument produktu

| Pole | Wartość |
| --- | --- |
| Status | Koncepcja produktu i zakres demonstracji hackathonowej |
| Nazwa robocza | Przejezdni |
| Główne miasto | Kraków |
| Obszar demonstracji | Centrum Krakowa |
| Główna grupa docelowa | Osoby poruszające się na wózkach |
| Ostatnia aktualizacja | 2026-10-03 |

Ten dokument opisuje, czym jest Przejezdni, jaki problem rozwiązuje, jak
powinien działać produkt docelowy oraz co rzeczywiście pokazujemy w
demonstracji. Jest źródłem decyzji produktowych. Szczegółowe scenariusze
demonstracji i aktorzy zostaną opisani w osobnym dokumencie.

## 1. Streszczenie

Przejezdni to aplikacja pomagająca osobom poruszającym się na wózkach
planować i modyfikować trasy po mieście. Nie ogranicza informacji o miejscu
do etykiety „dostępne” albo „niedostępne”. Pokazuje konkretne bariery,
ułatwienia, parametry nawierzchni i nachylenia oraz informuje, skąd pochodzi
każda informacja i jak bardzo można jej ufać.

Najważniejszy przepływ produktu wygląda następująco:

1. Użytkownik wybiera miejsce startowe i cel.
2. Ustawia parametry trasy zgodnie ze swoimi możliwościami i aktualną
   sytuacją.
3. Otrzymuje trasę wraz z listą znanych barier i ułatwień. Odcinki bez
   wystarczających danych nie są uwzględniane w trasie.
4. W czasie przejazdu może zgłosić napotkaną przeszkodę.
5. System uwzględnia zgłoszenie i proponuje objazd.
6. Zgłoszenie wzbogaca bazę informacji dla kolejnych użytkowników.

W demonstracji część tego przepływu będzie mockowana. Dane topograficzne i
mapowe są częściowo rzeczywiste, a część barier, takich jak schody, może być
odczytana bezpośrednio z danych mapowych. Przygotowana trasa, zgłoszenia,
wybrane fikcyjne utrudnienia i zachowanie mechanizmu wyznaczania trasy mogą być z góry
zdefiniowane na potrzeby prezentacji. Demo ma pokazać docelowe doświadczenie i ideę
produktu, a nie udawać gotowego systemu nawigacyjnego.

## 2. Problem

Osoba poruszająca się na wózku może zaplanować trasę, która na mapie wygląda
na krótką i możliwą do przejścia, ale w praktyce kończy się schodami,
wysokim krawężnikiem, zbyt dużym nachyleniem, nierówną nawierzchnią albo
zamkniętym przejściem. Taka przeszkoda może oznaczać konieczność zawrócenia,
wezwania pomocy lub rezygnacji z podróży.

Istniejące mapy i nawigacje zwykle:

- upraszczają dostępność do jednej wartości logicznej;
- nie pokazują wszystkich fizycznych cech trasy;
- nie rozróżniają informacji potwierdzonych od niezweryfikowanych;
- traktują brak danych jak brak problemu;
- nie pozwalają szybko zareagować na przeszkodę napotkaną na trasie;
- nie uwzględniają tego, że różne osoby mają różne możliwości i granice
  akceptowalnego ryzyka.

Przejezdni ma zmniejszać nieprzewidywalność podróży. Nie obiecuje, że każda
trasa będzie bez barier. Pomaga podjąć świadomą decyzję na podstawie
dostępnych danych i zmienić plan, gdy rzeczywistość różni się od mapy.

## 3. Wizja i obietnica produktu

### Wizja

Miasto, po którym osoba na wózku może poruszać się z większą niezależnością,
bo przed wyjazdem i w trakcie podróży zna nie tylko przebieg trasy, ale też
jej konkretne ograniczenia oraz poziom pewności informacji.

### Obietnica dla użytkownika

„Pokażemy Ci, co może wydarzyć się na trasie, pozwolimy dopasować ją do
Twoich potrzeb, a gdy napotkasz nieprzewidzianą przeszkodę, pomożemy znaleźć
alternatywę i przekażemy tę informację innym.”

### Zasady produktu

1. **Szczegóły zamiast uproszczeń** – informujemy o konkretnych barierach i
   ułatwieniach, a nie tylko o wyniku „dostępna/niedostępna”.
2. **Nieznane nie oznacza dostępne** – brak informacji zawsze pozostaje
   niepewnością i jest odpowiednio oznaczony.
3. **Użytkownik decyduje** – system proponuje trasę, ale użytkownik określa,
   które utrudnienia może zaakceptować.
4. **Dane mają pochodzenie** – przy szczegółach można sprawdzić źródło,
   datę pozyskania lub weryfikacji i status wiarygodności.
5. **Rzeczywistość może się zmienić** – zgłoszenia użytkowników są częścią
   modelu aktualizacji informacji.
6. **Dostępność dotyczy także aplikacji** – interfejs ma być użyteczny dla
   osób korzystających z klawiatury, czytnika ekranu i innych technologii
   asystujących.

## 4. Użytkownicy

### Główna grupa docelowa

Podstawowym użytkownikiem jest osoba poruszająca się na wózku, która chce
samodzielnie zaplanować przejazd po Krakowie albo zmienić trasę w jego
trakcie.

Nie zakładamy jednego profilu sprawności. Użytkownik może:

- poruszać się na wózku ręcznym albo elektrycznym;
- podróżować samodzielnie albo z pomocą drugiej osoby;
- mieć możliwość przejścia krótkiego odcinka bez wózka albo nie mieć takiej
  możliwości;
- akceptować niektóre bariery w określonych sytuacjach;
- mieć różną tolerancję nachylenia, nawierzchni i szerokości przejścia.

Nie chcemy zbierać wprost medycznej charakterystyki użytkownika. Zamiast
tego udostępniamy zestaw zrozumiałych parametrów trasy, które użytkownik
może samodzielnie ustawić.

### Użytkownicy drugorzędni i przyszli

- opiekun lub asystent planujący trasę dla osoby na wózku;
- zarządca obiektu, który chce przekazać informacje o dostępności;
- lokalna społeczność aktualizująca informacje o przeszkodach;
- organizator wydarzenia lub właściciel obiektu chcący udostępnić własny
  profil dostępności;
- miasta i organizacje wdrażające system na kolejnym obszarze.

## 5. Cele i poza zakresem

### Cele produktu

- ułatwić znalezienie trasy uwzględniającej indywidualne preferencje;
- pokazywać użytkownikowi konkretne bariery i ułatwienia na trasie;
- ujawniać niepewność, źródło i aktualność danych;
- umożliwić zgłoszenie przeszkody z aktualnej lokalizacji;
- doprowadzić do propozycji objazdu po zgłoszeniu bariery;
- budować użyteczną bazę danych społecznościowych bez ręcznego utrzymywania
  jej przez Urząd Miasta Krakowa;
- stworzyć rozwiązanie możliwe do przeniesienia do innych miast i obiektów
  prywatnych;
- zaprezentować ideę w sposób zrozumiały, wiarygodny i dostępny cyfrowo.

### Poza zakresem obecnej demonstracji

Poniższe elementy mogą zostać pokazane jako kierunek rozwoju, ale nie są
obietnicą działającej funkcji w obecnej wersji:

- dynamiczne wyznaczanie dowolnej trasy w czasie rzeczywistym;
- pełna nawigacja GPS;
- moderacja, reputacja i wieloetapowa weryfikacja zgłoszeń;
- obsługa wielu miast;
- pełne konta użytkowników, historia zgłoszeń i synchronizacja profilu;
- integracje z właścicielami obiektów lub systemami miejskimi;
- kompletna baza wszystkich miejsc dostępnych dla wózków;
- gwarantowanie, że zaproponowana trasa jest przejezdna w każdych warunkach.

## 6. Zakres demonstracji

### Co demonstracja ma pokazać

Demonstracja działa jak gotowa aplikacja, ale korzysta z kontrolowanego
zestawu danych i przygotowanych interakcji. Powinien pokazać:

- mapę centrum Krakowa z rzeczywistym podkładem lub danymi mapowymi;
- wybór punktu startowego i celu;
- przygotowaną trasę między punktami;
- filtry i parametry dopasowujące trasę do użytkownika;
- szczegółową listę odcinków, barier i ułatwień;
- warstwy mapy pokazujące wybrane informacje;
- symulowaną nawigację po trasie;
- fikcyjną przeszkodę, na przykład schody albo prace budowlane;
- szybkie zgłoszenie bariery z aktualnego miejsca;
- zmianę trasy po zgłoszeniu;
- informację, że zgłoszenie może zostać użyte przez innych użytkowników;
- źródło i status danych w panelu szczegółów.

### Dane demonstracyjne

W demonstracji należy rozróżnić trzy rodzaje danych:

| Rodzaj | Charakter | Sposób prezentacji |
| --- | --- | --- |
| Dane mapowe i topograficzne | Częściowo rzeczywiste, przygotowane skryptami | Z podaniem źródła i daty snapshotu |
| Trasa demonstracyjna | Z góry przygotowana na potrzeby prezentacji | „Trasa demonstracyjna na podstawie danych OSM” |
| Bariery, zgłoszenia i część zachowania systemu | Część barier pochodzi z danych mapowych; zgłoszenia, wybrane utrudnienia i część zachowania są fikcyjne lub mockowane | Jawnie oznaczone źródłem oraz jako demonstracyjne / niezweryfikowane, jeżeli dotyczy |

Fikcyjne dane są używane wyłącznie podczas demonstracji i nie będą częścią
wdrożenia produkcyjnego. Nie mogą być przedstawiane jako aktualne,
potwierdzone fakty.
Jeżeli demonstracja pokazuje fikcyjne utrudnienie, roboty drogowe albo
zgłoszenie, interfejs powinien oznaczyć ich demonstracyjny charakter. Bariery
odczytane z danych mapowych powinny zachować informację o źródle i dacie tych
danych.

### Wersja docelowa a demo

| Obszar | Demonstracja | Produkt docelowy |
| --- | --- | --- |
| Wyznaczanie trasy | Przygotowana trasa i kontrolowane scenariusze | Dynamiczne wyznaczanie trasy według parametrów użytkownika |
| GPS | Symulacja przejścia po trasie | Pozycja i nawigacja w czasie rzeczywistym |
| Zgłoszenia | Mockowany przepływ z natychmiastową zmianą trasy | Zgłoszenie zapisywane i dostępne dla innych użytkowników |
| Dane | OSM/topografia oraz dane fikcyjne | OSM, dane topograficzne, otwarte dane miejskie i crowdsourcing |
| Konta | Opcjonalnie jako kierunek rozwoju | Opcjonalne konto, historia i personalizacja |
| Obszar | Centrum Krakowa | Cały Kraków, później inne miasta i obiekty |

## 7. Główne doświadczenie użytkownika

### 7.1. Planowanie trasy

Użytkownik wskazuje początek i cel podróży. Może przejrzeć mapę oraz włączyć
interesujące go warstwy, a następnie ustawić parametry wyznaczania trasy.
System pokazuje propozycję wraz z podsumowaniem dystansu, przewidywanego
przebiegu oraz znanych utrudnień.

### 7.2. Poznanie trasy przed wyjazdem

Trasa jest prezentowana zarówno na mapie, jak i w formie tekstowej listy
odcinków. Każdy istotny odcinek może zawierać:

- typ nawierzchni i jej stan, jeżeli są znane;
- nachylenie;
- schody, rampę, windę, krawężnik lub inne ograniczenie;
- szerokość przejścia, jeżeli jest znana;
- dostępność przejścia dla pieszych;
- źródło, datę i status informacji w panelu szczegółów;
   - status wiarygodności informacji użytych do oceny danego odcinka.

### 7.3. Nawigacja

W demonstracji nawigacja jest symulowana. Użytkownik może przechodzić
przez kolejne odcinki, a interfejs wskazuje aktualne utrudnienia i
ułatwienia. Mapa nie jest jedynym nośnikiem informacji: każda istotna
informacja ma tekstowy odpowiednik.

### 7.4. Zgłoszenie nieprzewidzianej bariery

Podczas nawigacji użytkownik może zgłosić problem z aktualnego miejsca.
Minimalny przepływ obejmuje:

1. otwarcie akcji „Zgłoś utrudnienie”;
2. wybór kategorii bariery;
3. opcjonalne dodanie krótkiego opisu;
4. potwierdzenie zgłoszenia dla aktualnej lokalizacji lub odcinka;
5. prezentację statusu „do potwierdzenia”;
6. przedstawienie alternatywnej trasy w demonstracji.

W produkcie docelowym zgłoszenie powinno od razu wpływać na trasę jako
ostrzeżenie, ale nie powinno być prezentowane jako informacja zweryfikowana.

### 7.5. Zmiana decyzji podczas planowania

Użytkownik powinien móc wybrać konkretną barierę na mapie lub liście i:

- dopuścić ją, jeżeli jest w stanie ją pokonać lub ma pomoc;
- wykluczyć ją, jeżeli nie chce ryzykować;
- wykluczyć wszystkie bariery danego typu;
- zatwierdzić zmianę parametrów.

Po dopuszczeniu albo wykluczeniu bariery system powinien ponownie przeliczyć
trasę i zaproponować użytkownikowi zaktualizowany przebieg wraz z nową listą
barier i ułatwień.

Ta funkcja jest ważna, ponieważ „dostępność” nie jest identyczna dla każdego
użytkownika ani w każdej sytuacji.

## 8. Funkcjonalności produktu

### 8.1. Mapa

Mapa jest głównym miejscem poznawania przestrzeni, trasy i przeszkód. Powinna
obsługiwać:

- punkty startu i celu;
- przebieg trasy;
- punkty i odcinki związane z barierami oraz ułatwieniami;
- otwieranie szczegółów punktu lub odcinka;
- wskazanie aktualnego miejsca podczas nawigacji;
- dodanie zgłoszenia z bieżącej lokalizacji;
- alternatywny przebieg po zmianie parametrów.

### 8.2. Warstwy mapy

Warstwy służą do oglądania informacji. Same w sobie nie muszą zmieniać
wyniku wyznaczania trasy.

| Warstwa | Przykładowe informacje |
| --- | --- |
| Bariery i ułatwienia | Schody, rampy, windy, krawężniki, przejścia, ruchome schody |
| Nawierzchnia i nachylenie | Asfalt, kostka, żwir, piasek, gładkość, spadek |
| Dostępne POI | Muzea, miejsca odpoczynku, toalety i inne istotne miejsca |

Włączona warstwa musi mieć alternatywę tekstową. Użytkownik powinien móc
otrzymać tę samą informację z listy lub panelu, bez konieczności odczytywania
jej wyłącznie z mapy.

### 8.3. Parametry wyznaczania trasy

Parametry wyznaczania trasy wpływają na wybór trasy. Początkowe wartości domyślne,
przejęte z ustaleń projektu, są następujące:

| Parametr | Domyślne ustawienie |
| --- | --- |
| Maksymalne nachylenie | 6% |
| Schody | Nie akceptuj |
| Rampy | Akceptuj |
| Windy | Akceptuj |
| Ruchome schody | Nie akceptuj |
| Gładkie przejście dla pieszych | Preferuj / wymagaj zgodnie z trybem aplikacji |
| Wąski chodnik | Nie akceptuj |
| Asfalt | Akceptuj |
| Ścieżka | Akceptuj |
| Piasek | Nie akceptuj |
| Żwir | Nie akceptuj |
| Bruk / kocie łby | Nie akceptuj |

Wartości są hipotezą produktową do walidacji z użytkownikami. Nie opisują
medycznych możliwości osoby i nie powinny sugerować, że system zna jej stan
zdrowia.

### 8.4. Kategorie informacji o dostępności

Produkt powinien rozwijać model szczegółowych danych obejmujący co najmniej:

- schody i ich charakterystykę;
- nachylenie i spadek;
- rampy oraz windy;
- krawężniki (`kerb`);
- przejścia dla pieszych (`crossing`);
- oznaczenia dotykowe (`tactile_paving`);
- szerokość wejścia lub przejścia;
- rodzaj i gładkość nawierzchni (`surface`, `smoothness`);
- dostępne toalety;
- miejsca odpoczynku;
- inne POI istotne dla osoby na wózku;
- czasowe przeszkody, takie jak remonty lub zablokowane przejścia.

### 8.5. Punkty zainteresowania

POI mogą być pokazywane na mapie i w wynikach wyszukiwania. Szczegóły mogą
obejmować informację o dostępności dla wózków, wejściu, toalecie, miejscu
odpoczynku i źródle danych. Brak informacji o dostępności POI nie może być
interpretowany jako potwierdzenie dostępności.

## 9. Dane i wiarygodność

### 9.1. Źródła

Docelowy model danych może łączyć:

- OpenStreetMap;
- dane topograficzne, w tym informacje potrzebne do wyznaczania nachylenia;
- otwarte dane miejskie;
- zgłoszenia i korekty użytkowników;
- w przyszłości informacje przekazywane przez właścicieli lub zarządców
  obiektów.

Obecna baza zawiera już informacje o nachyleniu i nawierzchni. Możliwe, że
uda się również opracować dane o szerokości przejść. Są to parametry istotne
dla decyzji o trasie, ale ich minimalny wymagany zakres zostanie ustalony po
zakończeniu prowadzonego researchu.

System nie powinien wymagać ręcznej aktualizacji przez Miasto Kraków ani
dostępu do wewnętrznych systemów miejskich. Dane powinny być pobierane i
przetwarzane przez powtarzalne pipeline'y, niezależnie od warstwy prezentacji.

### 9.2. Proweniencja

Każda informacja o dostępności, barierze lub ułatwieniu powinna mieć:

- źródło informacji;
- datę pozyskania albo ostatniej weryfikacji;
- status wiarygodności;
- w przyszłości także identyfikator zgłoszenia lub snapshotu danych.

W interfejsie podstawowy widok może być zwięzły, ale panel szczegółów musi
pozwalać rozwinąć te informacje dla konkretnego elementu trasy lub mapy.

### 9.3. Statusy danych

Minimalny model statusów:

| Status | Znaczenie |
| --- | --- |
| Zweryfikowane | Informacja została potwierdzona zgodnie z przyjętym procesem. |
| Do potwierdzenia | Informacja pochodzi ze zgłoszenia lub innego źródła, ale nie została jeszcze potwierdzona. |
| Nieznane / brak danych | Nie mamy wystarczających informacji, aby ocenić element. |
| Demonstracyjne | Dane są fikcyjne albo przygotowane wyłącznie do prezentacji. |

Status „do potwierdzenia” nie może być wizualnie mylony ze statusem
„zweryfikowane”. To, czy odcinek z takim zgłoszeniem zostanie wykluczony z
trasy, powinno zależeć od ustawień użytkownika. W przyszłości na tę decyzję
może wpływać także ranking i wiarygodność osób zgłaszających. Status
„nieznane / brak danych” nie jest dowodem dostępności.

Poza obecną roadmapą można rozważyć potwierdzanie lub odrzucanie bariery
przez użytkownika znajdującego się w tym samym miejscu. Zgodne potwierdzenie
powinno zwiększać pewność informacji. Wpływ takiego potwierdzenia mógłby
zależeć od przyszłego rankingu i wiarygodności osoby potwierdzającej, ale
mechanizm rankingu nie jest obecnie planowanym elementem produktu.

### 9.4. Zasada brakujących danych

Domyślnie algorytm powinien wykluczać z wyznaczania trasy nieznane lub
niewystarczająco opisane odcinki. Jeżeli przez to nie da się znaleźć trasy
spełniającej parametry użytkownika, system powinien zakomunikować brak takiej
trasy i wyjaśnić, że przyczyną są ograniczenia danych lub wymagania trasy.
Nie wolno proponować trasy zawierającej odcinki bez wystarczających danych
tylko po to, aby zwrócić jakikolwiek wynik.

## 10. Dostępność cyfrowa i UX

Przejezdni powinien być projektowany zgodnie z WCAG 2.2 AA.

Wymagania podstawowe:

- pełna obsługa klawiaturą;
- widoczny i logiczny fokus;
- semantyczne kontrolki zamiast elementów klikalnych bez znaczenia;
- kompatybilność z czytnikami ekranu;
- odpowiedni kontrast tekstu, ikon i stanów;
- etykiety i komunikaty zrozumiałe bez polegania wyłącznie na kolorze;
- tekstowa lista trasy i barier jako alternatywa dla mapy;
- komunikaty o zmianie trasy i przyjęciu zgłoszenia przekazywane także
  użytkownikom technologii asystujących;
- możliwość zatrzymania, wznowienia i pominięcia animacji nawigacji;
- brak uzależnienia kluczowego działania od precyzyjnych gestów dotykowych;
- jasne rozróżnienie danych zweryfikowanych, niezweryfikowanych,
  nieznanych i demonstracyjnych.

Mapa nie może być jedynym sposobem zrozumienia trasy. Każda informacja
przedstawiona wizualnie powinna mieć odpowiednik tekstowy oraz nazwę możliwą
do odczytania przez czytnik ekranu.

## 11. Założenia techniczne produktu

### 11.1. Rozdzielenie danych od prezentacji

Pozyskiwanie i przetwarzanie danych powinno być oddzielone od frontendowej
prezentacji. Pipeline może przygotować graf, warstwy i metadane, natomiast
interfejs powinien otrzymywać stabilny model trasy i informacji o źródłach.

### 11.2. Wyznaczanie trasy w demonstracji

Pierwsza wersja demonstracyjna korzysta z jednej lub kilku przygotowanych
tras wyliczonych wcześniej na podstawie lokalnych danych OSM. Fixture trasy
powinien zawierać co najmniej:

- identyfikator trasy;
- punkty startu i celu;
- przebieg trasy;
- dystans;
- uporządkowane odcinki;
- znane nawierzchnie, nachylenia i bariery;
- źródło danych, datę snapshotu i status wiarygodności.

Dynamiczne wyznaczanie tras jest kolejnym etapem. Docelowo powinno uwzględniać
parametry użytkownika, nieznane dane, bariery czasowe i możliwość wyjaśnienia,
dlaczego wybrana trasa jest dłuższa lub omija konkretny element.

### 11.3. Rozszerzalność

Model produktu powinien pozwalać podmienić obszar danych bez przepisywania
całego interfejsu. Miasto lub prywatny zarządca powinien móc dostarczyć
własny zestaw danych, a aplikacja powinna zachować ten sam model źródeł,
statusów i szczegółów dostępności.

## 12. Model biznesowy i utrzymanie

Model biznesowy, źródła finansowania oraz sposób długoterminowego utrzymania
usługi zostaną opracowane w osobnym dokumencie. Ten dokument nie przesądza,
czy Przejezdni będzie usługą publiczną, rozwiązaniem dla miast, produktem dla
obiektów prywatnych czy modelem łączącym te kierunki.

Niezależnie od przyszłego modelu biznesowego podstawowa wiarygodność danych
nie może zależeć od ręcznej pracy jednego miasta. Konieczne są jasne źródła,
reprodukowalne aktualizacje i możliwość zgłaszania korekt.

## 13. Kryteria sukcesu

### Sukces demonstracji

Demonstracja spełnia cel, jeżeli odbiorca:

- rozumie problem nieprzewidywalnych barier;
- widzi, że trasa jest dopasowywana do preferencji użytkownika;
- potrafi odczytać bariery i ułatwienia poza samą mapą;
- rozumie różnicę między danymi zweryfikowanymi, niezweryfikowanymi,
  nieznanymi i demonstracyjnymi;
- widzi pełny przepływ: trasa → przeszkoda → zgłoszenie → objazd;
- rozumie, że produkt może działać w innych miastach i dla prywatnych
  obiektów;
- może obsłużyć kluczowy przepływ przy użyciu klawiatury i technologii
  asystujących.

### Docelowe miary do walidacji

Poza hackathonem warto mierzyć między innymi:

- odsetek tras zakończonych bez konieczności zawracania;
- liczbę i aktualność zgłoszeń barier;
- czas od zgłoszenia do jego potwierdzenia lub odrzucenia;
- liczbę użytkowników powracających do aplikacji;
- skuteczność znalezienia alternatywy po zgłoszeniu;
- zrozumienie statusów wiarygodności przez użytkowników;
- liczbę miast i obiektów możliwych do wdrożenia bez zmiany modelu produktu.

## 14. Ryzyka i sposoby ograniczania

| Ryzyko | Znaczenie | Sposób ograniczenia |
| --- | --- | --- |
| Nieaktualne dane OSM | Trasa może nie odpowiadać rzeczywistości | Pokazywać datę, źródło i status; umożliwić korekty |
| Brak danych oznaczony jak dostępność | Użytkownik może podjąć niebezpieczną decyzję | Jawny status „nieznane” i domyślne omijanie |
| Nadmiernie ambitne wyznaczanie tras | Ryzyko niedziałającego demo | Deterministyczne fixture'y i scenariusze |
| Różne potrzeby osób na wózkach | Jeden profil nie pasuje do wszystkich | Parametry akceptowanych barier zamiast jednej etykiety |
| Zgłoszenia niskiej jakości | Błędne objazdy i spadek zaufania | Status „do potwierdzenia”, później moderacja i potwierdzanie |
| Uzależnienie od mapy | Informacja może być niedostępna dla części użytkowników | Tekstowa alternatywa, klawiatura i czytniki ekranu |
| Ograniczenie danych do centrum Krakowa | Produkt może być mylnie uznany za kompletny | Jawnie opisać obszar demonstracji i plan skalowania |

## 15. Roadmapa

### Etap 1: demonstracja hackathonowa

- mapa centrum Krakowa;
- przygotowana trasa z prawdziwym podkładem lub danymi mapowymi;
- mockowane bariery i zgłoszenia;
- warstwy mapy;
- parametry wyznaczania trasy i ich wizualna obsługa;
- lista szczegółów trasy;
- symulowana nawigacja;
- przepływ zgłoszenia i objazdu;
- prezentacja źródeł, dat i statusów danych;
- podstawowa zgodność z WCAG 2.2 AA.

### Etap 2: działający prototyp

- dynamiczne wyznaczanie trasy na lokalnym grafie;
- stabilny model odcinka i wyjaśnienia decyzji mechanizmu wyznaczania trasy;
- reguły obsługi danych nieznanych i konfliktów źródeł;
- testy użyteczności mapy, prezentacji trasy i ustawień wyznaczania trasy z osobami
  z grupy docelowej;
- pełniejsze pokrycie Krakowa.

### Etap 3: rozwój usługi

- prawdziwa nawigacja GPS;
- opcjonalne konta, historia i profil ustawień;
- zapis zgłoszeń użytkowników;
- korekta istniejących danych;
- moderacja i obsługa potwierdzeń zgłoszeń;
- współpraca z właścicielami obiektów;

### Etap 4: dalszy rozwój w przyszłości

- wdrożenia w innych miastach;
- profile obiektów prywatnych i wydarzeń;
- zbadany model finansowania.

## 16. Otwarte pytania

- Które dane poza OSM i topografią będą dostępne w pierwszym produkcyjnym
  wdrożeniu?
- Jak dokładnie definiujemy „zweryfikowane” dla każdego typu źródła?
- Jak zaprojektować ranking i wiarygodność osób zgłaszających, aby pomagały
  oceniać zgłoszenia „do potwierdzenia”?
- Jakie minimalne informacje o szerokości, nachyleniu i nawierzchni są
  wystarczające do bezpiecznej decyzji? Pytanie pozostaje otwarte do czasu
  zakończenia researchu.
- Czy i w jaki sposób uwzględniać transport publiczny oraz torowiska?
- Jaki model biznesowy pozwoli utrzymać dane bez ograniczenia dostępu do
  podstawowej funkcji dla osób na wózkach?
- Jak zweryfikować domyślne 6% nachylenia i pozostałe ustawienia z osobami o
  różnych typach wózków?

## 17. Powiązane dokumenty

- `REQUIREMENTS.md` – wymagania konkursowe, kryteria dostępności i
  wiarygodności danych;
- `docs/scope.md` – pierwotne, robocze notatki dotyczące zakresu;
- `docs/routing.md` – analiza routingu i rekomendacja przygotowanej trasy
  demonstracyjnej;
- dokument scenariuszy i aktorów – do przygotowania osobno.
- dokument modelu biznesowego – do przygotowania osobno.
