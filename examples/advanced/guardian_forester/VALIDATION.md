# Weryfikacja — Guardian / Forester, 2026-09-28

Artefakty: `guardian_forester.samgraph`, `guardian_forester.json`, `guardian_forester.zip`.
Ten sam dokument jest sprawdzany w Studio oraz jako rzeczywisty zewnętrzny ZIP w Forge.

## Wykonane sprawdzenia

- Walidator Behavior Studio 1.2.0: zero błędów; dwa prawidłowe ostrzeżenia o trwałych zadaniach i wymaganych wbudowanych kontrolerach.
- 33 reguły, 506 węzłów, 473 połączenia; katalog 2, schemat paczki 1, format projektu 1.
- Pełna regresja Studio: **105/105 PASS** na Windows/Python 3.10, rzeczywisty Tk.
- Nowy scenariusz GUI: otwarcie samgraph, walidacja, EN/PL/DE, eksport JSON/ZIP, import JSON, wybór instancji, instalacja ZIP, potwierdzenie nadpisania i zachowanie backupu.
- Scenariusze negatywne GUI: błędny `@invented_role` blokuje eksport przed wyborem pliku; próba instalacji JSON obok istniejącego ZIP o tym samym ID jest odrzucona.
- Dodatkowe porównanie: dokument projektu, dostarczony JSON/ZIP oraz ZIP używany przez natywne testy mają identyczną treść Behavior.
- Cztery nowe testy arbitrażu Kotlin: pauza, nieznana skrzynia, brak zadania, bezpieczeństwo/kolejność reakcji.
- Trzy nowe testy ogólnej poprawki przygotowania: cooldown i pierwotny deadline po odczycie TaskCodec, gotowy/brakujący zasób, ręczna pauza.
- Skupiona kampania Forge: **10/10 wymaganych scenariuszy PASS**, w tym trzy nowe opisane poniżej. Po dodaniu trzech przypadków ścisły licznik bramki zmieniono z 7 na 10; żadnych testów ani asercji nie wyłączono.
- Podglądy `studio_preview.png` i `studio_validation.png` pochodzą z faktycznego okna Studio i zostały obejrzane.

## Trzy nowe dowody w świecie Forge

1. NPC z zużytą i nową siekierą oraz noszonym pancerzem/tarczą sam zakłada cztery elementy pancerza, tarczę i sprawną siekierę. Stara siekiera zostaje; żadne zadanie nie powstaje.
2. NPC z 35 stosami brukowca i bez siekiery rozładowuje tylko dopuszczony nadmiar, pobiera siekierę z autoryzowanej skrzyni, ścina i dostarcza dokładnie trzy kłody. Inny typ narzędzia zostaje w skrzyni, rezerwa brukowca jest zachowana, transfery i powroty mają rzeczywiste potwierdzenia.
3. Po fizycznym obrażeniu przez obserwowalnego moba NPC kontratakuje i obniża jego zdrowie. Po obniżeniu zdrowia NPC do 20% kasuje cel i przez dalsze 40 ticków nie atakuje. Testowy napastnik to nieruchoma krowa, aby pozostał obecny także przy pokojowym poziomie trudności areny; test nie symuluje naturalnego AI wroga.

## Błąd odkryty przez kombinację warunków

Osobne przygotowanie i rozładunek działały, lecz ich połączenie ujawniło wyścig:
po udanym UNLOAD, w istniejącym cooldownie, rodzic próbował ścinać bez siekiery,
zanim ENSURE mógł się rozpocząć. Ogólna poprawka w `TaskLogistics`/`TaskService`
wstrzymuje wykonanie rodzica tylko w tej przerwie, jeśli jawne przygotowanie jest
nadal niespełnione. Dotyczy dowolnego zapytania EnsureItems, bez rozgałęzienia na
konkretny przedmiot. Nie resetuje czasu, prób, cooldownu, stanu zadania ani transferów.
Core, API i formaty zapisów pozostają bez zmian.

## Końcowa pełna regresja

- `clean build`, granice modułów i dokładnie trzy JAR-y: **PASS**.
- Behavior: **422/422 testy jednostkowe PASS**.
- LLM: **200 PASS, 2 istniejące opcjonalne testy SKIPPED** (202 odkryte).
- Pełny natywny zestaw Behavior: **237/237 PASS**.
- Rzeczywisty klient: **13/13 scenariuszy PASS**, 13 zrzutów, fizyczne skutki, publiczne sterowanie/przypisania/zmiany zadań.
- Komenda zbiorcza zakończona `BUILD SUCCESSFUL in 10m 22s`.
- Core nie zmienił źródeł: jego testów jednostkowych nie powtarzano; wcześniejsze dowody są osobno w raporcie z 2026-09-27. Granice zależności sprawdzono ponownie.

## Granice dowodów

To nie jest pomiar poprawy Qwen ani nowego planera. Graf i naprawa działają deterministycznie.
Nie wszystkie kombinacje trasy patrolu, otoczenia, wielu dodatkowych modów i wyposażenia
przetestowano. Studio waliduje graf i kontrakt eksportu; fizyczne efekty potwierdzają
oddzielne natywne testy. Same reguły nie tworzą trwałych misji ani uprawnień do skrzyń.

Logi lokalne w `autonomy/`: `guardian-forester-studio.log`,
`guardian-forester-ui-workflow-final.log`, `guardian-forester-native-04.log`,
`guardian-forester-release.log`. Wczesne nieudane przebiegi zachowano jako dowód diagnozy;
nie są opisane jako zaliczone. Końcowy wynik całej regresji jest w PROJECT_STATE.md.
