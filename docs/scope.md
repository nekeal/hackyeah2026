# Scope projektu

Co jest ważne w projekcie:
- kod
- demo
- wideo
- link do repo/demo

## Źródła

- open street maps
- ...

## Kluczowe funkcjonalności

- Mapa z punktami i trasą
- Wyznaczanie trasy między wybranymi punktami
- Lista punktów na trasie (wskazówki trasy)
- Wyświetlanie ważnych punktów na mapie (od pewnego poziomu zbliżenia):
    - schody, rampy, windy, ruchome schody
    - 
- Informacje szczegółowe o punkcie
    - przystosowanie do wózków?
    - 
- Możliwość wykluczenia danego typu punktów przez akcję na punkcie 
    - wybieram punkt -> wyklucz ten typ punktów z trasy -> poszukiwania nowej trasy
- filtrowanie po kątach nachylenia (by default: max 6% nachylenia na trasie)
- Nawigacja na trasie z użyciem GPS
- Możliwość dodawania własnych punktów do trasy

# Moduły

- Mapa
- Punkty na mapie
    - Ułatwienia dostępu / Utrudnienia
    - Point of Interest
        - Czy jest dostepny dla wózków?
        - (Opcjonalnie) Punkt niedostępny dla wózków -> wskazówka dla zarządcy obiektu
- Wyznaczanie trasy pomiędzy wybranymi punktami na mapie
- Lista nawigacyjna z ułatwieniami i utrudnieniami
- (Opcjonalne) Nawigacja na trasie z GPS
- Zgłaszanie utrudnień/ułatwień na trasie (aka Yanosik)

Note: OSRM - Open Source Routing Machine

Jakie ustawienia filtrowania?
- max nachylenie - default: 6%
- schody - default: false
- rampy - default: true
- windy - default: true
- ruchome schody - default: false
- gładkie przejście dla pieszych - default: true
- wąski chodnik - default: false
- typ nawierzchni
    - piasek: false
    - żwir: false
    - bruk / kocie łby: false
    - asfalt: true
    - ścieżka: true

# High concept
 
System map do wyszukiwania tras dla osób poruszających się na wózkach z wyspecjalizowanymi filtrami ułatwień i utrudnień. Oparte o dane z OpenStreetMaps i dodatkowe informacje crowdsourcingowe od użytkowników aplikacji.

# Co musimy zrobić do mocka

- UI z mapą
- Ustawienie ogólnych filtrów (panel z opcjami)
- Wyszukiwanie trasy (lub dwóch)
- Wykluczenie utrudnienia (wszystkie schody) -> wyznaczenie nowej trasy
- Dodanie utrudnienia (wybrane jedne schody) -> wyznaczenie nowej trasy
- Nawigacja przez trasę
- Zgłoszenie utrudnienia -> wyznaczenie nowej trasy dla użytkownika z uwzględnieniem jego zgłoszenia (objazd)
- uwzględnic torowiska
