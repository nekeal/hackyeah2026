# Model biznesowy Przejezdni

## Teza

Przejezdni to bezpłatna aplikacja prospołeczna dla osób poruszających się na
wózkach. Pomaga zaplanować i zmienić trasę na podstawie indywidualnych
preferencji, pokazując konkretne bariery, ułatwienia, nachylenie, nawierzchnię
oraz źródło i aktualność danych.

Użytkownik nigdy nie płaci za podstawową funkcję. Utrzymanie projektu jest
finansowane instytucjonalnie: początkowo przez granty i dotacje, a docelowo
głównie przez API i usługi dla instytucji.

## Problem i wartość

Standardowe mapy nie pokazują wystarczająco szczegółowo fizycznych ograniczeń
trasy, nie rozróżniają danych pewnych od nieznanych i nie pozwalają szybko
zareagować na przeszkodę napotkaną podczas przejazdu.

Przejezdni zmniejszają nieprzewidywalność podróży poprzez:

- wyznaczanie trasy dopasowane do preferencji użytkownika;
- szczegółową listę etapów trasy, nie tylko jedną ocenę dostępności;
- jawne źródło, datę i status wiarygodności danych;
- zgłoszenia przeszkód i propozycję objazdu;
- traktowanie braku danych jako niepewności, a nie dostępności.

### Obietnica produktu

> „Pokażemy Ci, co może wydarzyć się na trasie, pozwolimy dopasować ją do
> Twoich potrzeb, a gdy napotkasz nieprzewidzianą przeszkodę, pomożemy znaleźć
> alternatywę i przekażemy tę informację innym.”

Ta obietnica jest nadrzędna wobec skróconych opisów wartości używanych w
częściach finansowej i instytucjonalnej. Model biznesowy finansuje właśnie ten
pełny przepływ: planowanie, reagowanie w trasie i wzbogacanie danych dla
kolejnych użytkowników.

## Użytkownicy i płatnicy

**Użytkownicy bezpłatni:**

- osoby korzystające z ręcznych i elektrycznych wózków;
- osoby podróżujące samodzielnie lub z asystentem;
- lokalna społeczność zgłaszająca bariery;
- zarządcy obiektów przekazujący korekty i informacje.

**Potencjalni płatnicy:**

- miasta i jednostki publiczne;
- fundacje oraz organizacje grantowe;
- hotele i operatorzy turystyczni;
- organizatorzy wydarzeń;
- instytucje kultury, sportu i rekreacji;
- operatorzy transportu i systemów informacji.

Płatnik finansuje dostęp do danych, integrację lub raport. Nie kupuje lepszego
statusu dostępności ani wyższej pozycji na mapie.

## Finansowanie

### Początek

- granty technologiczne i społeczne;
- dotacje miejskie i regionalne;
- programy publiczne dotyczące dostępności, mobilności i cyfryzacji;
- fundacje oraz sponsoring technologiczny.

### Cel długoterminowy

Większość kosztów utrzymania powinna docelowo pochodzić z usług
instytucjonalnych:

- API wyznaczania tras dostępnościowych;
- API danych o POI, barierach i proweniencji;
- integracje z systemami partnerów;
- raporty agregowane o barierach i jakości danych;
- narzędzia dla zarządców obiektów;
- planowanie dostępności wydarzeń i wybranych obszarów;
- opcjonalne audyty lub weryfikacje danych, jeśli potwierdzi je walidacja rynku.

API nie może tworzyć płatnej warstwy lepszych tras ani ograniczać publicznego
dostępu do aplikacji.

## Nienegocjowalne zasady

- Aplikacja dla użytkowników indywidualnych pozostaje bezpłatna.
- Statusu „dostępny” nie można kupić.
- Finansowanie nie może usuwać negatywnych zgłoszeń ani ukrywać niepewności.
- Każda informacja ma źródło, datę i status wiarygodności.
- Dane obliczeniowe są odróżnione od potwierdzenia terenowego.
- Dane o historii przemieszczania się użytkowników nie są sprzedawane.
- Miasto może finansować projekt, ale nie zarządza samodzielnie jego bazą ani
  kryteriami jakości.

## Zakres i dojrzałość produktu

Demonstracja hackathonowa obejmuje centrum Krakowa, przygotowane trasy oraz
częściowo mockowane zgłoszenia. Nie jest jeszcze gotową usługą komercyjną.

Produkt docelowy ma obejmować cały Kraków, a następnie inne miasta i prywatne
obiekty. Pokrycie techniczne siecią OSM nie oznacza pełnej weryfikacji terenowej.
Poziom danych musi być widoczny dla użytkownika.

Obecny prototyp pokazuje szczegóły etapów trasy i umożliwia lokalne wykluczenie
odcinka. Docelowy system raportów musi dodatkowo zapisywać zgłoszenia,
przekazywać je do moderacji i udostępniać ich status kolejnym użytkownikom.

## Model zaufania i governance

Przejezdni powinni działać jako niezależny podmiot, współpracujący z miastami,
ale niepodlegający jednemu finansującemu.

Potrzebne są:

- grupa konsultacyjna osób korzystających z wózków;
- udział organizacji społecznych w kryteriach jakości;
- publiczne zasady źródeł, statusów i konfliktu interesów;
- historia zmian krytycznych danych;
- moderacja zgłoszeń;
- w przyszłości reputacja użytkowników, ale bez zastępowania moderacji przy
  barierach wysokiego ryzyka.

## Etapy

1. **Demo:** centrum Krakowa, przygotowane scenariusze, szczegóły trasy,
   mockowane zgłoszenie i objazd.
2. **Prototyp:** dynamiczne wyznaczanie tras na lokalnym grafie, pełniejsze pokrycie
   Krakowa, testy z grupą docelową.
3. **Usługa:** trwałe raporty, moderacja, feedback po przejeździe, stabilny
   model danych i pierwsze płatne pilotaże API.
4. **Skalowanie:** inne miasta, obiekty prywatne, integracje i powtarzalny
   pipeline danych.

## Miary sukcesu

- zgodność informacji z rzeczywistością według anonimowego feedbacku;
- czas od zgłoszenia do potwierdzenia lub odrzucenia;
- odsetek zgłoszeń zaakceptowanych po moderacji;
- liczba tras i POI z kompletnym źródłem, datą i statusem;
- liczba użytkowników, którzy znaleźli alternatywę po zgłoszeniu bariery;
- udział przychodów z usług instytucjonalnych w kosztach utrzymania;
- liczba płatnych pilotaży lub integracji API.

Nie traktujemy liczby pobrań ani samej liczby decyzji miejskich jako dowodu
wartości produktu.

## Walidacja przed skalowaniem

Przed budową rozbudowanego API trzeba sprawdzić:

- czy instytucje mają konkretny budżet i właściciela problemu;
- za jakie dane lub funkcje są gotowe zapłacić;
- czy usługa może być finansowo utrzymywana bez opłat od użytkowników;
- czy osoby korzystające z wózków uznają informacje za przydatne i wiarygodne.

Minimalny cel walidacji: rozmowy z co najmniej 10 instytucjami, testy z co
najmniej 15 osobami z grupy docelowej oraz 3 konkretne deklaracje pilotażu,
budżetu lub współpracy.

## Główne ryzyka

- **Zależność od grantów:** grant finansuje rozwój, ale nie zapewnia ciągłości
  utrzymania.
- **Mała liczba zgłoszeń:** dane społecznościowe będą początkowo ograniczone;
  trzeba łączyć je z OSM, DEM i innymi źródłami.
- **Fałszywe poczucie bezpieczeństwa:** „przejezdna” nie może oznaczać
  bezwarunkowej gwarancji.
- **Konflikt interesów:** finansujący nie mogą wpływać na statusy i widoczność
  problemów.
- **Zbyt szeroka oferta:** najpierw należy zwalidować jeden produkt
  instytucjonalny, najlepiej API lub raporty, zamiast budować cały katalog usług.
