# Model biznesowy Przejezdni

## 1. Streszczenie

Przejezdni to bezpłatna, prospołeczna aplikacja webowa pomagająca osobom poruszającym się na wózkach planować przejazdy po mieście. Aplikacja nie upraszcza dostępności do etykiety „dostępne/niedostępne”. Pokazuje szczegóły każdego odcinka trasy: nachylenie, nawierzchnię, schody, krawężniki, udogodnienia, braki danych oraz źródło i datę danych.

Aplikacja ma być zawsze bezpłatna dla użytkowników indywidualnych. Utrzymanie projektu będzie finansowane instytucjonalnie: początkowo głównie z grantów, dotacji i finansowania publicznego, a docelowo w możliwie dużej części z płatnego API oraz usług powiązanych dla instytucji.

Przejezdni pozostają niezależni od pojedynczego miasta. Miasto może finansować rozwój i korzystać z danych, ale nie może kupić pozytywnego statusu dostępności, usunąć niekorzystnego zgłoszenia ani przejąć kontroli nad kryteriami wiarygodności.

## 2. Problem

Osoba korzystająca z wózka często nie potrzebuje ogólnej informacji, czy miejsce lub trasa jest „dostępna”. Potrzebuje wiedzieć:

- czy konkretny odcinek ma schody lub wysoki krawężnik;
- jakie jest nachylenie odcinka;
- jaka jest nawierzchnia i jej przewidywana trudność;
- czy występuje winda, rampa albo inne udogodnienie;
- które dane pochodzą z pomiaru, OSM, zgłoszenia użytkownika lub innego źródła;
- kiedy dane były ostatnio aktualizowane;
- gdzie występuje niepewność i jakiego rodzaju jest to ryzyko.

Brak takiej informacji może powodować rezygnację z podróży albo dotarcie do bariery, której użytkownik nie mógł wcześniej przewidzieć.

Miasta i zarządcy obiektów również nie mają kompletnego, aktualnego i ustrukturyzowanego obrazu barier. Zgłoszenia mieszkańców są rozproszone, trudne do porównywania i często nie zawierają informacji przydatnych do routingu.

## 3. Wartość dla użytkowników

Główna obietnica produktu:

> Przejezdni pomagają zaplanować trasę dopasowaną do indywidualnych preferencji, pokazując szczegóły i niepewność każdego jej odcinka zamiast ukrywać je za jedną etykietą dostępności.

Użytkownik otrzymuje:

- darmowe wyznaczenie trasy po całym Krakowie;
- ustawienie własnego limitu nachylenia i tolerancji wybranych barier;
- informację o każdym etapie przejazdu, także wtedy, gdy trasa została zaklasyfikowana jako przejezdna;
- możliwość wykluczenia problematycznego odcinka i przeliczenia objazdu;
- widoczne źródło, datę oraz status danych;
- możliwość zgłoszenia problemu napotkanego na trasie.

„Przejezdna” nie oznacza „bezwarunkowo bezpieczna”. Oznacza, że trasa spełnia określone kryteria algorytmu przy dostępnych danych. Szczegóły odcinków i poziom niepewności pozostają widoczne.

## 4. Użytkownicy i płatnicy

### Użytkownicy bezpłatni

- osoby korzystające z ręcznych i elektrycznych wózków;
- osoby podróżujące samodzielnie;
- osoby podróżujące z asystentem;
- opiekunowie i asystenci;
- osoby zgłaszające bariery i udogodnienia.

Nie zakładamy jednego profilu użytkownika wózka. Parametry trasy mają być indywidualnymi preferencjami, a nie diagnozą ani kategorią medyczną.

### Instytucje finansujące lub kupujące usługi

- miasta i jednostki publiczne;
- organizacje grantowe i fundacje;
- zarządcy obiektów publicznych;
- hotele i operatorzy turystyczni;
- organizatorzy wydarzeń;
- operatorzy transportu i systemów informacji miejskiej;
- instytucje kultury, sportu i rekreacji.

Płatnikiem nie musi być użytkownik aplikacji. Płatnikiem jest instytucja, która potrzebuje danych, integracji, raportu albo dowodu wpływu swoich działań na dostępność.

## 5. Model finansowania

### Etap początkowy

Główne źródła finansowania:

- granty technologiczne i społeczne;
- dotacje miejskie i regionalne;
- programy publiczne związane z dostępnością, mobilnością i cyfryzacją;
- fundacje i organizacje wspierające osoby z niepełnosprawnościami;
- sponsoring technologiczny i finansowanie określonych prac, np. moderacji danych dla wybranego obszaru.

Finansowanie publiczne może wspierać rozwój i utrzymanie systemu, ale nie może uzależniać kryteriów danych od decyzji jednego miasta.

### Model docelowy

Docelowo główną część kosztów utrzymania powinny pokrywać usługi instytucjonalne, przy zachowaniu bezpłatnego dostępu publicznego:

- API routingu dostępnościowego;
- API danych o POI, barierach i proweniencji;
- integracje z miejskimi, turystycznymi i instytucjonalnymi systemami informacji;
- raporty agregowane o barierach i jakości danych;
- narzędzia dla zarządców obiektów do przeglądania i aktualizacji informacji o własnych obiektach;
- planowanie dostępnych tras dla wydarzeń i obszarów czasowo zmiennych;
- audyty lub weryfikacje danych, których wyniki pozostają niezależne od płatnika.

API i usługi nie mogą ograniczać podstawowego dostępu użytkowników indywidualnych ani tworzyć płatnej warstwy lepszych tras dla instytucji.

## 6. Zasady komercjalizacji

Obiekt lub instytucja może zapłacić za audyt, integrację, API albo raport. Nie może zapłacić za:

- status „dostępny”;
- wyższą pozycję w wynikach;
- usunięcie negatywnego zgłoszenia;
- pominięcie niepewności danych;
- zmianę parametrów routingu na korzystniejsze dla obiektu.

Jeśli instytucja finansuje rozwój konkretnego obszaru, informacja o finansowaniu może być jawna. Nie może ona wpływać na wynik oceny dostępności.

Dane o przemieszczaniu się osób nie będą sprzedawane. Raporty dla instytucji mogą korzystać wyłącznie z danych zagregowanych i odpowiednio zanonimizowanych.

## 7. Zasięg i pokrycie danych

Pierwsza wersja ma obejmować cały Kraków, ale pokrycie będzie opisywane na kilku niezależnych poziomach:

- **pokrycie techniczne**: część sieci pieszej OSM znajdująca się w grafie routingu;
- **pokrycie informacyjne**: część odcinków z informacją o istotnych parametrach;
- **pokrycie zweryfikowane terenowo lub społecznościowo**: część danych potwierdzona przez zgłoszenie, moderatora, audytora albo inne źródło wyższego zaufania;
- **pokrycie użytkowe**: część kluczowych relacji między punktami, dla których można wskazać trasę z jasno opisanymi ograniczeniami.

System może mieć techniczny graf całego Krakowa, ale nie będzie twierdził, że każdy odcinek jest fizycznie zweryfikowany. Brak danych jest prezentowany jako niepewność i domyślnie może wykluczać odcinek z trasy.

Priorytet weryfikacji powinny mieć:

- szpitale i przychodnie;
- urzędy;
- dworce i główne węzły transportowe;
- muzea, teatry, opera i filharmonia;
- stadiony, obiekty sportowe i rekreacyjne;
- ważne miejsca turystyczne;
- trasy łączące powyższe punkty z transportem publicznym.

Priorytet nie oznacza automatycznego pozytywnego statusu. Oznacza tylko pierwszeństwo w pozyskiwaniu i sprawdzaniu danych.

## 8. Dane, raporty i moderacja

Obecny prototyp pokazuje szczegóły odcinków trasy, m.in. nawierzchnię, maksymalne nachylenie, schody, krawężniki, braki danych oraz proweniencję całej trasy. Użytkownik może lokalnie wykluczyć odcinek i przeliczyć objazd.

To nie jest jeszcze trwały system raportowania. Obecnie wykluczenie odcinka nie tworzy zapisanego zgłoszenia, nie trafia do moderatora i nie zmienia późniejszych tras innych użytkowników.

Docelowy raport powinien zawierać co najmniej:

- lokalizację i kierunek przejazdu;
- rodzaj problemu lub udogodnienia;
- datę obserwacji;
- opcjonalne zdjęcie lub dodatkowy opis;
- informację, czy problem jest stały, czasowy czy niepewny;
- źródło zgłoszenia i historię jego weryfikacji.

Model moderacji:

- początkowo zgłoszenia weryfikują moderatorzy;
- później reputacja użytkownika może priorytetyzować zgłoszenia i ograniczać pracę moderatorów;
- reputacja nie zastępuje moderacji przy krytycznych barierach;
- sprzeczne zgłoszenia muszą być widoczne i rozstrzygane przez procedurę;
- zaufanie do informacji powinno maleć wraz z jej wiekiem lub zmianą warunków;
- każda zmiana danych musi mieć historię i źródło.

Wolontariusze mogą w przyszłości dostarczać dane podczas codziennego poruszania się po mieście. Powinien to być osobny program z instrukcją raportowania, kryteriami jakości i metodą kontroli błędów, a nie nieformalna zamiana moderatorów na przypadkowych użytkowników.

## 9. Różnica między obliczeniem a weryfikacją terenową

Dane wyliczone z OSM i modelu wysokościowego mogą być technicznie przetworzone, ale nie są tym samym co weryfikacja w terenie.

System musi rozróżniać co najmniej:

- źródło danych, np. OSM, DEM, zgłoszenie użytkownika, audyt;
- sposób pozyskania, np. obliczenie, obserwacja, zdjęcie, import;
- datę pozyskania lub weryfikacji;
- status, np. zweryfikowane obliczeniowo, potwierdzone terenowo, zgłoszone, nieznane, sporne;
- aktualność informacji.

Obecny komunikat `Zweryfikowano numerycznie (DEM + OSM tags)` powinien być rozumiany jako weryfikacja obliczenia, nie jako potwierdzenie realnego stanu w terenie. To rozróżnienie jest ważne dla wiarygodności, komunikacji i przyszłych usług API.

## 10. Wartość dla miasta i instytucji

Miasto otrzymuje:

- ustrukturyzowane zgłoszenia o barierach, zamiast niejednorodnych sygnałów;
- mapę miejsc i odcinków o największej niepewności;
- możliwość priorytetyzacji interwencji infrastrukturalnych;
- publiczny, niezależny kanał informacji o przejezdności;
- możliwość udostępnienia mieszkańcom aktualnych danych bez ręcznego utrzymywania całej bazy;
- mierzalne informacje o czasie obsługi i powtarzalności problemów.

Prywatny zarządca obiektu otrzymuje:

- możliwość sprawdzenia, jakie informacje o obiekcie widzi użytkownik;
- API lub eksport danych do własnego systemu;
- możliwość zgłoszenia korekty i dostarczenia dowodów;
- raport braków informacyjnych i barier w otoczeniu;
- większą przewidywalność obsługi osób z ograniczoną mobilnością.

Instytucja nie otrzymuje prawa do kształtowania wyniku oceny.

## 11. Wskaźniki sukcesu

Wskaźniki operacyjne:

- liczba kilometrów sieci dostępnej w grafie routingu;
- procent odcinków ze wskazanym źródłem i datą;
- liczba POI z kompletem wymaganych pól;
- liczba zgłoszeń problemów i udogodnień;
- odsetek zgłoszeń zaakceptowanych, odrzuconych lub wymagających dodatkowej weryfikacji;
- mediana czasu od zgłoszenia do decyzji moderatora;
- wiek najstarszych danych w obszarach priorytetowych.

Wskaźniki wartości dla użytkownika:

- liczba tras spełniających zadane preferencje bez użycia danych nieznanych;
- odsetek zgłoszeń użytkowników potwierdzających niezgodność informacji z rzeczywistością;
- anonimowy feedback po przejeździe dotyczący zgodności informacji ze stanem faktycznym;
- liczba przypadków, w których użytkownik zgłosił problem i otrzymał przeliczony objazd;
- liczba powtarzających się problemów na tej samej trasie.

Wskaźniki finansowania:

- liczba aktywnych grantów i partnerów finansujących;
- udział przychodów z usług instytucjonalnych w kosztach utrzymania;
- liczba płatnych integracji API;
- liczba instytucji korzystających z danych bez wpływu na ich statusy;
- długość finansowanego okresu utrzymania systemu.

Nie należy traktować liczby pobrań aplikacji ani liczby decyzji miejskich jako głównych dowodów wpływu. Są trudne do interpretacji i nie pokazują, czy informacje były trafne.

## 12. Prywatność

Przejezdni nie będą przechowywać historii tras ani budować nieanonimowych profili zachowania użytkowników bez wyraźnej i koniecznej podstawy.

Zasady:

- minimalizacja zbieranych danych;
- brak historii tras domyślnie;
- anonimowe lub pseudonimowe zgłoszenia tam, gdzie jest to możliwe;
- ograniczona retencja danych lokalizacyjnych;
- brak sprzedaży danych o przemieszczaniu się;
- agregowanie danych przed udostępnieniem instytucjom;
- jasna informacja o tym, jakie dane są potrzebne do moderacji i reputacji;
- analiza ryzyka ochrony danych przed uruchomieniem trwałego systemu raportów.

Brak przetwarzania diagnoz medycznych nie oznacza automatycznie braku ryzyk prywatności. Lokalizacja, preferencje tras i zgłoszenia mogą pośrednio ujawniać wrażliwe informacje.

## 13. Niezależność i zarządzanie

Projekt powinien mieć niezależne zasady zarządzania danymi i kryteriami jakości. Miasto może być ważnym partnerem, klientem lub grantodawcą, ale nie powinno być jedynym właścicielem ani moderatorem systemu.

Rekomendowane elementy governance:

- publiczna polityka źródeł i statusów danych;
- publiczna historia zmian krytycznych informacji;
- grupa konsultacyjna osób korzystających z wózków;
- udział organizacji społecznych w definiowaniu kryteriów jakości;
- jawne zasady konfliktu interesów dla finansujących;
- niezależna procedura odwołań od decyzji moderacyjnych;
- okresowy raport o jakości danych i finansowaniu.

Grono ekspertów powinno obejmować osoby korzystające z różnych typów wózków, organizacje społeczne, osoby zajmujące się dostępnością cyfrową, ekspertów GIS/routingu oraz osoby odpowiedzialne za prywatność i prawo.

## 14. Walidacja modelu

Przed inwestowaniem w płatne API należy sprawdzić, czy instytucje rzeczywiście mają budżet i potrzebę zakupu takiej usługi.

Minimalny plan walidacji:

- rozmowy z co najmniej 10 potencjalnymi instytucjami finansującymi lub kupującymi usługi;
- rozmowy i testy z co najmniej 15 osobami korzystającymi z wózków;
- sprawdzenie, czy instytucje potrafią wskazać konkretny budżet, właściciela problemu i termin decyzji;
- uzyskanie co najmniej 3 deklaracji pilotażu lub listów intencyjnych przed budową rozbudowanego API;
- test jednego raportu miejskiego opartego na danych z aplikacji;
- pomiar zgodności danych z rzeczywistością na ograniczonej grupie tras priorytetowych.

Sama deklaracja „miasto byłoby zainteresowane” nie jest walidacją. Walidacją jest wskazany budżet, osoba decyzyjna, zakres pilotażu albo podpisana deklaracja współpracy.

## 15. Etapy rozwoju

### Etap 1: prototyp publiczny

- bezpłatne wyznaczanie tras w Krakowie;
- szczegóły każdego etapu trasy;
- parametry indywidualnych preferencji;
- widoczna proweniencja i niepewność danych;
- techniczna baza pod zgłoszenia.

### Etap 2: wiarygodne raportowanie

- trwałe zgłoszenia problemów i udogodnień;
- moderacja;
- historia zmian;
- feedback po przejeździe;
- rozróżnienie danych obliczeniowych i terenowych;
- współpraca z organizacjami osób z niepełnosprawnościami.

### Etap 3: usługi instytucjonalne

- stabilne API routingu i danych;
- autoryzacja, limity i monitoring użycia;
- eksporty i raporty agregowane;
- integracje z systemami partnerów;
- narzędzia dla zarządców obiektów;
- pierwsze płatne pilotaże.

### Etap 4: skalowanie między miastami

- powtarzalny pipeline danych;
- konfiguracja źródeł i kryteriów dla nowego miasta;
- niezależne wdrożenia bez ręcznego utrzymywania danych przez miasto;
- wspólne standardy proweniencji, statusów i raportowania;
- model finansowania lokalnego wdrożenia bez utraty niezależności projektu.

## 16. Najważniejsze ryzyka

### Zależność od grantów

Granty finansują rozwój, ale nie gwarantują wieloletniego utrzymania. Należy stopniowo zwiększać udział usług instytucjonalnych albo utrzymywać wieloletni portfel finansowania publicznego.

### Niska liczba zgłoszeń

Mała społeczność nie zapewni szybkiego pokrycia terenowego. Dlatego podstawą musi być transparentne łączenie OSM, danych wysokościowych, danych miejskich, obserwacji użytkowników i zaplanowanych działań wolontariuszy.

### Fałszywe poczucie bezpieczeństwa

Etykieta „przejezdna” może zostać błędnie odczytana jako gwarancja. Szczegóły każdego odcinka, daty, źródła i ograniczenia muszą być ważniejsze niż kolor statusu.

### Konflikt interesów finansujących

Instytucja może próbować wpłynąć na swój status albo widoczność problemów. Zasady finansowania, moderacji i statusów muszą to uniemożliwiać technicznie i organizacyjnie.

### Odpowiedzialność za aktualność danych

Warunki terenowe się zmieniają. System powinien pokazywać wiek danych, obsługiwać zgłoszenia nieaktualności i nie sugerować trwałego certyfikatu.

### Zbyt szeroki zakres

Cały Kraków jako graf techniczny jest rozsądnym celem. Ręczna weryfikacja wszystkiego nie jest. Należy jasno rozdzielić skalę techniczną od priorytetu jakościowego.

## 17. Decyzje do dalszej walidacji

- forma prawna i zasady własności projektu;
- minimalny roczny budżet utrzymania;
- definicja pierwszego komercyjnego API;
- kryteria i poziomy statusów danych;
- zasady reputacji użytkowników;
- zakres danych przechowywanych przy feedbacku po przejeździe;
- lista pierwszych tras i POI do weryfikacji;
- partnerzy organizacji społecznych i skład grupy konsultacyjnej.
