HELP = {}

HELP['pl'] = '''SAMCNPC BEHAVIOR STUDIO · HOW-TO

1. Start
Program otwiera przykład Podążanie. Wybierz węzeł, zmień parametry w Inspektorze i kliknij Zastosuj. Dwuklik w bibliotece dodaje nowy węzeł.

2. Graf
Typowy układ: Warunek → AND/OR/NOT → Reguła → Akcja. Przeciągnij prawy port do lewego portu. AND/OR przyjmują 1..16 warunków, NOT dokładnie jeden. Reguła ma jeden warunek i 1..16 akcji.

3. To nie są execution pins z Unreal
Przewód Reguła → Akcja oznacza kandydaturę akcji, nie sekwencję. Runtime wybiera niekolidujące akcje według priorytetów i kanałów. Błąd akcji nie uruchamia automatycznie „else” w tym samym ticku.

4. Obsługa płótna
LPM: wybór/przeciąganie. Środkowy przycisk albo Spacja+LPM: przesuwanie. Kółko: zoom. F: dopasuj. Delete: usuń. Ctrl+Z/Ctrl+Y: cofanie/ponawianie. Ctrl+S: zapis projektu. F1: ta pomoc.

5. Pliki
.samgraph zachowuje układ edytora. .json to właściwa paczka Behavior. ZIP zawiera behaviors/*.json. Instaluj go bez wypakowywania w <instancja>/resources/samcnpc/behaviors/.

6. Instalacja
Gotowy JSON trafia do:
  <instancja>/config/samcnpc/behaviors/<plik>.json
Następnie w grze jako operator:
  /samcnpc behavior reload
  /samcnpc behavior packs
  /samcnpc behavior assign Sam example:follow
  /samcnpc behavior diagnostics Sam
Nie wkładaj behavior JSON do resourcepacks/datapacks — aktualny loader ich tam nie odkrywa.

7. Drwal
Przykład demo_lumberjack pokazuje tylko regułę always → run_lumberjack_demo. Właściwa logika drwala jest w Kotlinie. Sam JSON nie tworzy joba. Demo uruchamia:
  /samcnpc behavior lumberjack Sam

8. Bezpieczeństwo
Studio używa tylko zarejestrowanych warunków i akcji bieżącego katalogu Behavior (wersja 2). Nie wykonuje Pythona z paczek, nie wysyła komend do Minecrafta i nie modyfikuje JAR-ów. Ostateczną walidacją pozostaje /samcnpc behavior reload w grze.
'''

HELP['en'] = '''SAMCNPC BEHAVIOR STUDIO · HOW-TO

1. Start
The app opens the Follow example. Select a node, edit its values in Inspector and press Apply. Double-click the node library to add components.

2. Graph
Typical structure: Condition → AND/OR/NOT → Rule → Action. Drag an output port to an input port. AND/OR accept 1..16 conditions, NOT exactly one. A rule has one condition and 1..16 actions.

3. These are not Unreal execution pins
Rule → Action means “this action is a candidate while the rule matches”, not “run after the previous action”. The runtime arbitrates non-conflicting actions by priorities and channels. A failed action does not automatically run an else branch in the same tick.

4. Canvas controls
LMB: select/drag. Middle mouse or Space+LMB: pan. Wheel: zoom. F: fit graph. Delete: remove selected node/edge. Ctrl+Z/Ctrl+Y: undo/redo. Ctrl+S: save project. F1: open this help.

5. Files
.samgraph stores editor layout. .json is the actual Behavior pack. ZIP contains behaviors/*.json. Install it without unpacking in <instance>/resources/samcnpc/behaviors/.

6. Installation
Put the exported JSON in:
  <instance>/config/samcnpc/behaviors/<file>.json
Then as an operator in game:
  /samcnpc behavior reload
  /samcnpc behavior packs
  /samcnpc behavior assign Sam example:follow
  /samcnpc behavior diagnostics Sam
Do not put Behavior JSON in resourcepacks/datapacks; the current loader does not discover it there.

7. Lumberjack
The demo_lumberjack reference only shows always → run_lumberjack_demo. The real lumberjack algorithm lives in Kotlin and the JSON does not create its job. Start the existing demo with:
  /samcnpc behavior lumberjack Sam

8. Safety
Studio exposes only registered conditions/actions from the current registered Behavior catalog (version 2). It does not execute Python from packs, send Minecraft commands, or modify JARs. The final authoritative validation remains /samcnpc behavior reload.
'''

HELP['de'] = '''SAMCNPC BEHAVIOR STUDIO · HOW-TO

1. Start
Die App öffnet das Beispiel „Folgen“. Knoten auswählen, Werte im Inspektor ändern und Übernehmen drücken. Ein Doppelklick in der Knotenbibliothek fügt Komponenten hinzu.

2. Graph
Typischer Aufbau: Bedingung → AND/OR/NOT → Regel → Aktion. Ausgangsport auf Eingangsport ziehen. AND/OR akzeptieren 1..16 Bedingungen, NOT genau eine. Eine Regel besitzt eine Bedingung und 1..16 Aktionen.

3. Keine Unreal-Execution-Pins
Regel → Aktion bedeutet: Die Aktion ist ein Kandidat, solange die Regel passt. Es ist keine Sequenz. Die Runtime wählt nicht kollidierende Aktionen anhand von Prioritäten und Kanälen. Ein Fehler löst im selben Tick nicht automatisch einen else-Zweig aus.

4. Bedienung
LMT: auswählen/ziehen. Mittlere Taste oder Leertaste+LMT: verschieben. Mausrad: Zoom. F: Graph einpassen. Delete: Knoten/Verbindung löschen. Ctrl+Z/Ctrl+Y: rückgängig/wiederholen. Ctrl+S: speichern. F1: Hilfe.

5. Dateien
.samgraph speichert das Editor-Layout. .json ist das echte Behavior-Pack. ZIP enthält behaviors/*.json. Ohne Entpacken unter <Instanz>/resources/samcnpc/behaviors/ installieren.

6. Installation
Exportiertes JSON nach:
  <Instanz>/config/samcnpc/behaviors/<Datei>.json
Danach im Spiel als Operator:
  /samcnpc behavior reload
  /samcnpc behavior packs
  /samcnpc behavior assign Sam example:follow
  /samcnpc behavior diagnostics Sam
Behavior-JSON nicht in resourcepacks/datapacks ablegen; der aktuelle Loader sucht dort nicht.

7. Holzfäller
Die demo_lumberjack-Referenz zeigt nur always → run_lumberjack_demo. Der eigentliche Algorithmus liegt in Kotlin; das JSON erzeugt keinen Job. Das vorhandene Demo startet mit:
  /samcnpc behavior lumberjack Sam

8. Sicherheit
Studio zeigt nur registrierte Bedingungen/Aktionen aus dem aktuellen registrierten Behavior-Katalog (Version 2). Es führt keinen Python-Code aus Packs aus, sendet keine Minecraft-Befehle und verändert keine JARs. Die endgültige Prüfung bleibt /samcnpc behavior reload im Spiel.
'''

HELP['en'] += """
9. Inventory and tools
Use inventory_count and equipment_matches with an exact item ID or an authoritative role such as @axe. minecraft:coal excludes charcoal. ensure_equipment equips a suitable carried item; it does not take items from chests. Authorized durable ENSURE/preparation tasks handle chest collection, reserves, backups and safe free-slot recovery. Unknown container stock is not empty.

10. Catalog and ZIP
File → Load registered catalog reads the matching Behavior registered schema. Invalid candidates retain the current catalog; your graph stays intact. Choose an instance root in Installation; JSON goes to config/samcnpc/behaviors/, ZIP directly to resources/samcnpc/behaviors/. Keep one active source per pack ID. Invalid reloads retain the last good registry. See the 1.2.0 manuals for the chest → tool → work tutorial.
"""

HELP['pl'] += """
9. Ekwipunek i narzędzia
Użyj inventory_count i equipment_matches z dokładnym ID lub rolą, np. @axe. minecraft:coal wyklucza charcoal. ensure_equipment wyposaża noszony przedmiot, nie pobiera ze skrzyni. Uprawniony trwały ENSURE/przygotowanie obsługuje źródła, rezerwy, zapas i bezpieczne wolne miejsca. Nieznana skrzynia nie jest pusta.

10. Katalog i ZIP
Plik → Wczytaj zarejestrowany katalog czyta schemat zgodnego Behavior. Błąd zachowuje poprzedni katalog, graf pozostaje. W Instalacji wybierz instancję; JSON trafia do config/samcnpc/behaviors/, ZIP bezpośrednio do resources/samcnpc/behaviors/. Jedno aktywne źródło na ID. Błędny reload zachowuje ostatni poprawny rejestr. Instrukcje 1.2.0 zawierają ćwiczenie skrzynia → narzędzie → praca.
"""

HELP['de'] += """
9. Inventar und Werkzeuge
inventory_count und equipment_matches verwenden exakte IDs oder Rollen wie @axe. minecraft:coal schließt charcoal aus. ensure_equipment rüstet getragene Gegenstände aus, holt aber nichts aus Truhen. Erlaubte dauerhafte ENSURE/Vorbereitung bearbeitet Quellen, Reserven, Ersatz und sichere freie Plätze. Unbekannte Truhen sind nicht leer.

10. Katalog und ZIP
Datei → Registrierten Katalog laden liest das passende Behavior-Schema. Fehler behalten den alten Katalog; der Graph bleibt erhalten. Unter Installation die Instanz wählen: JSON nach config/samcnpc/behaviors/, ZIP direkt nach resources/samcnpc/behaviors/. Eine aktive Quelle je ID. Fehlerhafte Reloads behalten den letzten gültigen Bestand. Handbücher 1.2.0 enthalten die Übung Truhe → Werkzeug → Arbeit.
"""
