<p align="center">
  <img src="assets/samcnpc_behavior_studio_logo.png" width="720" alt="SAMCNPC Behavior Studio" />
</p>

# SAMCNPC Behavior Studio

[English](README.md) | Polski | [Deutsch](README_DE.md)

**Edytor wizualny offline do deterministycznych paczek zachowań NPC — SAMCNPC dla Minecraft Forge 1.20.1.**

Łącz warunki i akcje, sprawdzaj wynikowy JSON, waliduj graf i instaluj paczkę w swojej
instancji Minecraft. Studio **1.3.0** ma ciemny edytor węzłów, interfejs EN/PL/DE,
przykłady oraz trzy ilustrowane poradniki GitHub. Do edycji paczek nie trzeba programować.

SAMCNPC Core zapewnia ciało i mechanikę NPC,
a SAMCNPC Behavior wykonuje reguły i trwałe zadania.
Studio przygotowuje ich dane. Działa bez Minecrafta, modelu LLM, kluczy API i usług chmurowych.

## Możliwości

- Ciemny edytor warunków, grup `all` / `any` / `not`, reguł i akcji; priorytety, cooldown i kanały.
- Projekty `.samgraph` w zgodnym formacie 1, import JSON, cofanie zmian i podgląd eksportu.
- Pola generowane z zarejestrowanego schematu: typy, granice, wybory, opisy, wartości domyślne
  i kanały. Bieżący katalog: **25 warunków, 25 akcji, 17 referencji paczek wbudowanych**.
- Fakty ekwipunku, wolnych miejsc, wyposażenia i trwałości, dozwolone obserwacje skrzyń,
  stan zadania, pozycja, przyczyny błędu i akcja `ensure_equipment`.
- Domyślny angielski; przełączanie EN/PL/DE bez przebudowy okna i utraty grafu, szkiców czy historii.
- Walidacja, eksport JSON/ZIP, wybór głównego katalogu instancji, kontrola duplikatów i backup
  po potwierdzonym nadpisaniu.
- Pomoc, informacje o programie, projekty ćwiczeń i zaawansowany graf liczący 506 węzłów.

Graf opisuje **warunki → regułę → kandydatów na akcje**. Połączenia nie są programem
wykonywanym po kolei. Behavior wybiera akcje według priorytetów i zajętych kanałów.
Pobieranie narzędzi ze skrzyni i wznowienie dłuższej pracy wykorzystują istniejące trwałe
zadania. JSON/ZIP nie tworzy nowego algorytmu, kodu, komend ani uprawnień do skrzyń.

## Uruchomienie

Potrzebny jest **Python 3.10+ z Tkinterem/Tcl/Tk** i pulpitem graficznym.
Edytor korzysta wyłącznie z biblioteki standardowej — nie ma kroku `pip install`.

```powershell
git clone https://github.com/DasIstEin20/SAMCNPC_Behavior_Studio.git
cd SAMCNPC_Behavior_Studio
.\START_WINDOWS.bat
```

Możesz też uruchomić `python studio.py`, a na Linux/macOS `python3 studio.py`.
Nie potrzeba Javy, Forge, submodułów Git ani sąsiedniego repozytorium SAMCNPC do pracy w edytorze.

1. Przez **Plik → Otwórz** wczytaj [przykład podążania](examples/custom/example_follow.samgraph).
2. Zmień parametr, zastosuj go, sprawdź graf i obejrzyj podgląd JSON.
3. Zapisz `.samgraph` do dalszej edycji, a następnie wyeksportuj JSON albo ZIP.

W grze potrzebujesz pasujących Core + Behavior oraz Kotlin for Forge na Minecraft Forge
**1.20.1**. Behavior musi obsługiwać dołączony **katalog 2** i zewnętrzne ZIP-y.
Schema/semantyka paczki pozostaje w wersji **1**. Sam numer wersji rozwojowego JAR-a
nie gwarantuje zgodności z nowymi komponentami; sprawdź katalog właściwego buildu.

## Poradniki

| English | Polski | Deutsch |
| --- | --- | --- |
| [Read the guide](tutorials/GUIDE_EN.md) | [Czytaj poradnik](tutorials/GUIDE_PL.md) | [Handbuch lesen](tutorials/GUIDE_DE.md) |

Trzy strony Markdown zastępują sześć wariantów PDF White/Black. GitHub używa Twojego
jasnego albo ciemnego motywu. Każdy poradnik zachowuje **20 oryginalnych rozdziałów**,
komendy, rzeczywiste zrzuty i klikalny spis treści; dodano rozdział o Guardian / Forester.

Tematy: budowanie reguł, ekwipunek, wyposażenie, dokładne przedmioty i role, skrzynie,
bezpieczny rozładunek, priorytety, konflikty kanałów, eksport ZIP, instalacja i diagnostyka.
Ćwiczenie praktyczne prowadzi przez „NPC potrzebuje narzędzia → pobiera je z dozwolonej
skrzyni → wyposaża → wykonuje pracę”. [Projekty ćwiczeń](tutorials/examples/) są dołączone.

## Przykłady

- [Podążanie](examples/custom/example_follow.samgraph), [ostrożne podążanie](examples/custom/example_cautious_follow.samgraph)
  i [odwet](examples/custom/example_retaliate.samgraph).
- [Przygotowanie narzędzia](examples/custom/example_tool_preparation.samgraph): założenie sprawnej siekiery już noszonej przez NPC.
- [Guardian / Forester](examples/advanced/guardian_forester/guardian_forester.samgraph): **33 reguły, 506 węzłów, 473 połączenia**
  obejmujące bezpieczeństwo, odwet, wyposażenie, trwałą logistykę i eskortę.

Zaawansowany przykład ma eksporty JSON/ZIP, [polską instrukcję](examples/advanced/guardian_forester/README_PL.md). Otwórz go przez
**Plik → Otwórz**. Samo przypisanie paczki nie tworzy misji ani dostępu do skrzyń.

![Guardian / Forester w rzeczywistym oknie Studio](examples/advanced/guardian_forester/studio_preview.png)

## Eksport i instalacja

Po walidacji eksportuj JSON albo ZIP. W zakładce Instalacja wybierz **główny katalog instancji**,
a Studio utworzy właściwą ścieżkę:

| Format | Miejsce instalacji |
| --- | --- |
| JSON | `<instancja>/config/samcnpc/behaviors/<nazwa>.json` |
| ZIP | `<instancja>/resources/samcnpc/behaviors/<nazwa>.zip` — bez wypakowywania |

ZIP zawiera `behaviors/<nazwa>.json` i instrukcje instalacji. To zewnętrzny zasób SAMCNPC,
nie vanilla resource pack ani datapack. Projekt `.samgraph` zapisuj osobno.
W multiplayer pliki muszą trafić do **instancji serwera**.

Jedno ID paczki może występować tylko w jednym aktywnym źródle — nie instaluj równocześnie
JSON i ZIP tej samej paczki. Nadpisanie wymaga potwierdzenia i zachowuje backup.
Po instalacji przykładu narzędzia użyj w grze:

```text
/samcnpc behavior reload
/samcnpc behavior packs
/samcnpc behavior assign Sam example:tool_preparation
/samcnpc behavior diagnostics Sam
```

Podstaw imię swojego NPC. Reload wymaga operatora, operacje NPC stosują uprawnienia
przywołującego/operatora. `assign` zastępuje listę paczek; zachowaj kontrolery wymagane
przez aktywne zadanie. Błędny reload pozostawia ostatni poprawny rejestr.
Szczegóły: [format ZIP i limity](docs/EXTERNAL_BEHAVIOR_ZIPS.md).

## Katalog i zapytania o przedmioty

Wiążący [zarejestrowany schemat](vendor/behavior-pack-registered.schema.json) jest dołączony.
**Plik → Wczytaj zarejestrowany katalog** przyjmuje zgodny schemat Behavior z katalogu `contracts`.
Błędny kandydat nie zastępuje aktywnego katalogu. Odświeżenie dotyczy bieżącej sesji;
sprawdź graf przed eksportem. Aktualizacja katalogu w dystrybucji:

```text
python make_catalog.py <sciezka-repozytorium-lub-schematu>
python make_schema.py
```

`minecraft:coal` nie obejmuje charcoal; `@axe` oznacza autorytatywną rolę siekiery;
`minecraft:coal|minecraft:charcoal` jawnie dopuszcza oba. `ensure_equipment` dobiera noszone
wyposażenie. Skrzynia i rozładunek wymagają dozwolonej trwałej operacji oraz jawnej polityki.
Nieznana zawartość skrzyni nie oznacza zera. [Opis kontraktów](docs/LOCAL_AUTONOMY.md).

## Weryfikacja

Uruchom z katalogu tego repozytorium:

```text
python -m unittest discover -s tests -v
python cli.py examples/custom/example_follow.samgraph --json-out follow.json --zip-out follow.zip
```

Testy GUI wymagają pulpitu; na bezekranowym Linux użyj Xvfb. Sam CLI nie importuje Tkintera.
wyników Forge/klienta. Walidator Studio sprawdza kontrakt grafu; skutki fizyczne trzeba
potwierdzić przez reload i test w Minecraft. Testowy ZIP jest dołączony, więc zestaw nie
wymaga sąsiedniego katalogu Behavior.

## Licencja

[MIT](LICENSE).

## Widok misji: prawdziwe połączenia paczek

Otwórz Plik -> Misja. Osobne okno edytuje projekt .sammission; przewody akcji zwykłego .samgraph nadal oznaczają równoległe propozycje. Etapy łączy Po potwierdzonym sukcesie. Po błędzie misja zatrzymuje się do przeglądu; liczba ponowień etapu wynosi zero.

[Tutorial](examples/missions/tutorial.sammission) · [Full mission](examples/missions/full.sammission) · [ZIP](examples/missions/tutorial.zip)

Ekwipunek, wyposażenie, zapas w celu, przygotowana gleba i bezpieczne dojście opisują bieżący stan. Są sprawdzane ponownie na końcu misji. Usunięcie dostarczonych kłód może unieważnić warunek zapasu. Sukces zadania jest historycznym potwierdzeniem konkretnego zlecenia, nie dowodem innych zapasów.
