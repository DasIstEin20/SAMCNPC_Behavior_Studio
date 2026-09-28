"""UI localization for SAMCNPC Behavior Studio.
Runtime behavior IDs and exported JSON are language-neutral and never translated.
"""
from __future__ import annotations

DEFAULT_LANGUAGE = 'en'

LANGUAGES = {
    'en': 'English',
    'pl': 'Polski',
    'de': 'Deutsch',
}

STRINGS = {
'pl': {
    'file':'Plik','new':'Nowy','open':'Otwórz JSON / projekt…','save':'Zapisz projekt…','save_as':'Zapisz projekt jako…','export_json':'Eksport JSON…','export_zip':'Eksport ZIP…','close':'Zamknij',
    'examples':'Przykłady','edit':'Edycja','undo':'Cofnij   Ctrl+Z','redo':'Ponów   Ctrl+Y','auto_layout':'Automatyczny układ','fit_view':'Dopasuj widok','language':'Język',
    'header_subtitle':'BEHAVIOR STUDIO  /  GRAF REGUŁ','btn_export_zip':'Eksport ZIP','btn_export_json':'Eksport JSON','btn_validate':'Sprawdź paczkę','btn_save':'Zapisz projekt',
    'tab_graph':'Graf reguł','tab_json':'JSON i walidacja','tab_install':'Instalacja','tab_help':'Pomoc / How-to','tab_about':'O programie',
    'node_library':'BIBLIOTEKA WĘZŁÓW','add_selected':'+ Dodaj wybrany węzeł','rules_in_pack':'REGUŁY W PACZCE','new_rule':'+ Nowa reguła',
    'tool_undo':'↶ Cofnij','tool_redo':'↷ Ponów','tool_layout':'Ułóż','tool_fit':'Dopasuj','tool_delete':'Usuń',
    'legend_condition':'● warunek','legend_rule':'   ● reguła','legend_action':'   ● akcja','offline_snapshot':'registered catalog · v2',
    'pack':'PACZKA','pack_id':'ID paczki','pack_priority':'Priorytet paczki','description':'Opis','auto_channels':'Kanały automatycznie z akcji','apply_pack':'Zastosuj dane paczki',
    'inspector':'INSPEKTOR','select_node':'Wybierz węzeł na płótnie. Dwuklik w palecie dodaje nowy.','rule_id':'ID reguły','priority':'Priorytet','cooldown':'Cooldown [ticki]','apply_node':'Zastosuj parametry węzła','delete_node':'Usuń węzeł',
    'json_refresh':'Graf → JSON (odśwież)','json_apply':'JSON → graf (zastosuj edycję)','copy_json':'Kopiuj JSON','json_draft_note':'Edycja tutaj wymaga zastosowania przed eksportem.',
    'install_title':'Instalacja do config, nie do resourcepacks','install_desc':'Wybierz katalog gry/instancji lub serwera, który zawiera folder config. Program nie wykonuje poleceń w grze.',
    'choose_instance':'Wybierz instancję…','npc_label':'NPC (nazwa bez spacji / UUID):','install_current':'Instaluj bieżący JSON…','refresh_instructions':'Odśwież instrukcję','copy_commands':'Kopiuj polecenia reload / assign / diagnostics',
    'logic_all':'AND · wszystkie','logic_any':'OR · co najmniej jeden','logic_not':'NOT · zaprzeczenie','new_rule_title':'Nowa reguła',
    'cat_condition':'WARUNEK','cat_action':'AKCJA','cat_rule':'REGUŁA','cat_logic':'LOGIKA',
    'canvas_header':'WARUNKI  →  REGUŁY  →  KANDYDATURY AKCJI','canvas_hint':'rolka: zoom  ·  Spacja + LPM: przesuwanie','connect_hint':'Połącz z portem wejściowym · Esc anuluje',
    'ctx_delete_node':'Usuń węzeł','ctx_delete_edge':'Usuń połączenie','ctx_add_rule':'Dodaj regułę tutaj','ctx_add_and':'Dodaj AND','ctx_add_or':'Dodaj OR','ctx_add_not':'Dodaj NOT',
    'connected':'Połączono węzły.','error_prefix':'BŁĄD: ','status_counts':'{conditions} warunków · {actions} akcji · {builtins} builtinów | catalog 2 | offline',
    'rule_channel_warning':'Akcje konkurują o kanały. To nie jest sekwencja po zakończeniu kroku.','advanced_warning':'Nie tworzysz tu zadania. Potrzebny aktywny task/job oraz oryginalna paczka sterująca.',
    'logic_help':'Połącz wyjścia warunków z lewym portem. Prawy port połącz z kolejnym wyrażeniem lub Regułą.',
    'move_up':'↑ Wyżej','move_down':'↓ Niżej','no_args':'bez argumentów','range':'Zakres: {min} .. {max}','default':' (domyślnie: {value})',
    'about_title':'SAMCNPC Behavior Studio','about_desc':'Graficzny, offline’owy kreator paczek zachowań dla SAMCNPC Behavior. Łączy zarejestrowane warunki i akcje w graf reguł, waliduje schemaVersion 1 oraz eksportuje JSON do config/samcnpc/behaviors/ lub ZIP do resources/samcnpc/behaviors/. Nie wykonuje skryptów, nie łączy się z LLM i nie zmienia JAR-ów.','about_version':'Behavior Studio 1.3.0 · snapshot Behavior b92ec0e','about_languages':'Interfejs: Polski · English · Deutsch','about_license':'Narzędzie: MIT · runtime SAMCNPC pozostaje oddzielnym projektem.',
    'lang_pending':'Najpierw zastosuj albo odrzuć bieżące zmiany w JSON/Inspektorze przed zmianą języka.',
    'validation_ok':'OK — brak lokalnych błędów.','copied':'Skopiowano do schowka.',
},
'en': {
    'file':'File','new':'New','open':'Open JSON / project…','save':'Save project…','save_as':'Save project as…','export_json':'Export JSON…','export_zip':'Export ZIP…','close':'Exit',
    'examples':'Examples','edit':'Edit','undo':'Undo   Ctrl+Z','redo':'Redo   Ctrl+Y','auto_layout':'Auto layout','fit_view':'Fit view','language':'Language',
    'header_subtitle':'BEHAVIOR STUDIO  /  RULE GRAPH','btn_export_zip':'Export ZIP','btn_export_json':'Export JSON','btn_validate':'Validate pack','btn_save':'Save project',
    'tab_graph':'Rule graph','tab_json':'JSON & validation','tab_install':'Install','tab_help':'Help / How-to','tab_about':'About',
    'node_library':'NODE LIBRARY','add_selected':'+ Add selected node','rules_in_pack':'RULES IN PACK','new_rule':'+ New rule',
    'tool_undo':'↶ Undo','tool_redo':'↷ Redo','tool_layout':'Layout','tool_fit':'Fit','tool_delete':'Delete',
    'legend_condition':'● condition','legend_rule':'   ● rule','legend_action':'   ● action','offline_snapshot':'registered catalog · v2',
    'pack':'PACK','pack_id':'Pack ID','pack_priority':'Pack priority','description':'Description','auto_channels':'Derive channels from actions','apply_pack':'Apply pack metadata',
    'inspector':'INSPECTOR','select_node':'Select a node on the canvas. Double-click the palette to add one.','rule_id':'Rule ID','priority':'Priority','cooldown':'Cooldown [ticks]','apply_node':'Apply node parameters','delete_node':'Delete node',
    'json_refresh':'Graph → JSON (refresh)','json_apply':'JSON → graph (apply edit)','copy_json':'Copy JSON','json_draft_note':'Edits here must be applied before export.',
    'install_title':'Install to config, not resourcepacks','install_desc':'Choose the game/instance or server root that contains the config folder. The program does not execute in-game commands.',
    'choose_instance':'Choose instance…','npc_label':'NPC (name without spaces / UUID):','install_current':'Install current JSON…','refresh_instructions':'Refresh instructions','copy_commands':'Copy reload / assign / diagnostics commands',
    'logic_all':'AND · all','logic_any':'OR · any','logic_not':'NOT · negate','new_rule_title':'New rule',
    'cat_condition':'CONDITION','cat_action':'ACTION','cat_rule':'RULE','cat_logic':'LOGIC',
    'canvas_header':'CONDITIONS  →  RULES  →  ACTION CANDIDATES','canvas_hint':'wheel: zoom  ·  Space + LMB: pan','connect_hint':'Connect to an input port · Esc cancels',
    'ctx_delete_node':'Delete node','ctx_delete_edge':'Delete connection','ctx_add_rule':'Add rule here','ctx_add_and':'Add AND','ctx_add_or':'Add OR','ctx_add_not':'Add NOT',
    'connected':'Nodes connected.','error_prefix':'ERROR: ','status_counts':'{conditions} conditions · {actions} actions · {builtins} built-ins | catalog 2 | offline',
    'rule_channel_warning':'Actions compete for channels. This is not a sequence that waits for the previous step to finish.','advanced_warning':'This does not create a task. An active task/job and the original controller pack are required.',
    'logic_help':'Connect condition outputs to the left port. Connect the right port to another expression or a Rule.',
    'move_up':'↑ Up','move_down':'↓ Down','no_args':'no arguments','range':'Range: {min} .. {max}','default':' (default: {value})',
    'about_title':'SAMCNPC Behavior Studio','about_desc':'Offline visual editor for SAMCNPC Behavior packs. It combines registered conditions and actions into rule graphs, validates schemaVersion 1, and exports JSON to config/samcnpc/behaviors/ or ZIP to resources/samcnpc/behaviors/. It never executes scripts, talks to an LLM, or modifies mod JARs.','about_version':'Behavior Studio 1.3.0 · Behavior catalog 2','about_languages':'Interface: Polski · English · Deutsch','about_license':'Tool license: MIT · the SAMCNPC runtime remains a separate project.',
    'lang_pending':'Apply or discard current JSON/Inspector edits before changing the interface language.',
    'validation_ok':'OK — no local errors.','copied':'Copied to clipboard.',
},
'de': {
    'file':'Datei','new':'Neu','open':'JSON / Projekt öffnen…','save':'Projekt speichern…','save_as':'Projekt speichern unter…','export_json':'JSON exportieren…','export_zip':'ZIP exportieren…','close':'Beenden',
    'examples':'Beispiele','edit':'Bearbeiten','undo':'Rückgängig   Ctrl+Z','redo':'Wiederholen   Ctrl+Y','auto_layout':'Automatisch anordnen','fit_view':'Ansicht einpassen','language':'Sprache',
    'header_subtitle':'BEHAVIOR STUDIO  /  REGELGRAPH','btn_export_zip':'ZIP exportieren','btn_export_json':'JSON exportieren','btn_validate':'Pack prüfen','btn_save':'Projekt speichern',
    'tab_graph':'Regelgraph','tab_json':'JSON & Prüfung','tab_install':'Installation','tab_help':'Hilfe / How-to','tab_about':'Über',
    'node_library':'KNOTENBIBLIOTHEK','add_selected':'+ Ausgewählten Knoten hinzufügen','rules_in_pack':'REGELN IM PACK','new_rule':'+ Neue Regel',
    'tool_undo':'↶ Rückgängig','tool_redo':'↷ Wiederholen','tool_layout':'Anordnen','tool_fit':'Einpassen','tool_delete':'Löschen',
    'legend_condition':'● Bedingung','legend_rule':'   ● Regel','legend_action':'   ● Aktion','offline_snapshot':'registered catalog · v2',
    'pack':'PACK','pack_id':'Pack-ID','pack_priority':'Pack-Priorität','description':'Beschreibung','auto_channels':'Kanäle aus Aktionen ableiten','apply_pack':'Pack-Daten übernehmen',
    'inspector':'INSPEKTOR','select_node':'Wähle einen Knoten auf der Fläche. Doppelklick in der Palette fügt einen hinzu.','rule_id':'Regel-ID','priority':'Priorität','cooldown':'Cooldown [Ticks]','apply_node':'Knotenparameter übernehmen','delete_node':'Knoten löschen',
    'json_refresh':'Graph → JSON (aktualisieren)','json_apply':'JSON → Graph (Änderung übernehmen)','copy_json':'JSON kopieren','json_draft_note':'Änderungen hier müssen vor dem Export übernommen werden.',
    'install_title':'Installation in config, nicht in resourcepacks','install_desc':'Wähle das Hauptverzeichnis der Spielinstanz oder des Servers mit dem Ordner config. Das Programm führt keine Befehle im Spiel aus.',
    'choose_instance':'Instanz wählen…','npc_label':'NPC (Name ohne Leerzeichen / UUID):','install_current':'Aktuelles JSON installieren…','refresh_instructions':'Anleitung aktualisieren','copy_commands':'reload / assign / diagnostics kopieren',
    'logic_all':'AND · alle','logic_any':'OR · mindestens eins','logic_not':'NOT · negieren','new_rule_title':'Neue Regel',
    'cat_condition':'BEDINGUNG','cat_action':'AKTION','cat_rule':'REGEL','cat_logic':'LOGIK',
    'canvas_header':'BEDINGUNGEN  →  REGELN  →  AKTIONSKANDIDATEN','canvas_hint':'Mausrad: Zoom  ·  Leertaste + LMT: verschieben','connect_hint':'Mit Eingangsport verbinden · Esc bricht ab',
    'ctx_delete_node':'Knoten löschen','ctx_delete_edge':'Verbindung löschen','ctx_add_rule':'Regel hier hinzufügen','ctx_add_and':'AND hinzufügen','ctx_add_or':'OR hinzufügen','ctx_add_not':'NOT hinzufügen',
    'connected':'Knoten verbunden.','error_prefix':'FEHLER: ','status_counts':'{conditions} Bedingungen · {actions} Aktionen · {builtins} Built-ins | Katalog 2 | offline',
    'rule_channel_warning':'Aktionen konkurrieren um Kanäle. Das ist keine Sequenz, die auf den vorherigen Schritt wartet.','advanced_warning':'Hier wird kein Task erzeugt. Ein aktiver Task/Job und das originale Controller-Pack sind erforderlich.',
    'logic_help':'Verbinde Bedingungsausgänge mit dem linken Port. Den rechten Port mit einem weiteren Ausdruck oder einer Regel verbinden.',
    'move_up':'↑ Höher','move_down':'↓ Tiefer','no_args':'keine Argumente','range':'Bereich: {min} .. {max}','default':' (Standard: {value})',
    'about_title':'SAMCNPC Behavior Studio','about_desc':'Offline-Grafikeditor für SAMCNPC-Behavior-Packs. Er verbindet registrierte Bedingungen und Aktionen zu Regelgraphen, prüft schemaVersion 1 und exportiert JSON nach config/samcnpc/behaviors/ oder ZIP nach resources/samcnpc/behaviors/. Er führt keine Skripte aus, verbindet sich nicht mit einem LLM und verändert keine Mod-JARs.','about_version':'Behavior Studio 1.3.0 · Behavior-Katalog 2','about_languages':'Oberfläche: Polski · English · Deutsch','about_license':'Tool-Lizenz: MIT · die SAMCNPC-Runtime bleibt ein separates Projekt.',
    'lang_pending':'Bitte aktuelle JSON-/Inspektor-Änderungen zuerst übernehmen oder verwerfen, bevor die Sprache gewechselt wird.',
    'validation_ok':'OK — keine lokalen Fehler.','copied':'In die Zwischenablage kopiert.',
}}

EXAMPLE_LABELS = {
'Podążanie — pierwszy działający przykład': {
    'pl':'Podążanie — pierwszy działający przykład','en':'Follow — first working example','de':'Folgen — erstes funktionierendes Beispiel'},
'Ostrożne podążanie — warunek zdrowia': {
    'pl':'Ostrożne podążanie — warunek zdrowia','en':'Cautious follow — health condition','de':'Vorsichtig folgen — Gesundheitsbedingung'},
'Odwet melee — kilka reguł': {
    'pl':'Odwet melee — kilka reguł','en':'Melee retaliation — multiple rules','de':'Nahkampf-Vergeltung — mehrere Regeln'},
'Drwal: demo — referencja wbudowana': {
    'pl':'Drwal: demo — referencja wbudowana','en':'Lumberjack: demo — built-in reference','de':'Holzfäller: Demo — Built-in-Referenz'},
'Drwal: task i przerwania — referencja': {
    'pl':'Drwal: task i przerwania — referencja','en':'Lumberjack: task & interruptions — reference','de':'Holzfäller: Task & Unterbrechungen — Referenz'},
}

# Catalog UI translations. IDs remain canonical and are never translated in exported JSON.
CATALOG = {
'en': {
'samcnpc:always':('Always','Condition that is always true.'),
'samcnpc:has_summoner':('Has summoner','NPC has a bound summoner UUID. This does not mean the player is currently observable.'),
'samcnpc:summoner_online':('Summoner available','The summoner is a living player available in the bounded Behavior observation.'),
'samcnpc:distance_to_summoner':('Distance to summoner','Compares horizontal distance to the observed summoner.'),
'samcnpc:has_unhandled_damage':('New damage','A new damage event that has not yet been handled by the reaction memory.'),
'samcnpc:has_attack_target':('Has combat target','Behavior currently holds a living combat target; it does not search for a new enemy.'),
'samcnpc:target_alive':('Target is alive','The current combat target is still alive.'),
'samcnpc:was_hurt_recently':('Recently hurt','Checks the age of the most recent damage event.'),
'samcnpc:health_fraction':('Health fraction','Fraction of maximum health; 0.3 means 30%.'),
'samcnpc:task_ready':('Task ready','An existing task is ready for an execution step. Does not create a task.'),
'samcnpc:task_combat_ready':('Combat interruption ready','The current combat task/interruption is ready.'),
'samcnpc:task_reaction_ready':('Task reaction ready','The existing task policy reports a ready reaction.'),
'samcnpc:task_inventory_ready':('Task logistics ready','An existing inventory-work task is ready.'),
'samcnpc:task_inventory_requested':('Task requests logistics','The existing task requests a logistics interruption.'),
'samcnpc:look_at_summoner':('Look at summoner','Turns the view toward the observed summoner.'),
'samcnpc:look_at_target':('Look at target','Turns the view toward the current combat target.'),
'samcnpc:move_to_summoner':('Follow summoner','Navigates toward the player with hysteresis. Empty startDistance means stopDistance + 2.'),
'samcnpc:move_to_target':('Approach combat target','Moves toward the current combat target; this is not a new navigation task.'),
'samcnpc:stop_movement':('Stop movement','Releases current movement control.'),
'samcnpc:attack_target':('Attack target','Melee attack on the current target using real cooldown, reach and Core mechanics.'),
'samcnpc:set_attack_target_from_recent_attacker':('Select recent attacker','Selects an eligible attacker from a new damage event. Does not search for the nearest enemy.'),
'samcnpc:clear_attack_target':('Clear combat target','Clears the transient Behavior combat target.'),
'samcnpc:begin_task_inventory':('Begin logistics interruption','Continues an existing execution; does not create an operation.'),
'samcnpc:run_inventory_task':('Inventory task step','Continues an existing inventory task/interruption.'),
'samcnpc:begin_task_reaction':('Begin task reaction','Continues an existing execution; does not create an operation.'),
'samcnpc:run_combat_task':('Combat task step','Continues an existing combat task/interruption.'),
'samcnpc:run_navigation_task':('Navigation task step','Continues an existing navigation task.'),
'samcnpc:run_delivery_task':('Delivery / transport step','Continues an existing delivery/transport task.'),
'samcnpc:run_mining_task':('Mining task step','Continues an existing mining task.'),
'samcnpc:run_food_task':('Food task step','Continues an existing food acquisition task.'),
'samcnpc:run_explorer_task':('Explorer task step','Continues an existing exploration task.'),
'samcnpc:run_fishing_task':('Fishing task step','Continues an existing fishing task.'),
'samcnpc:run_machine_task':('Machine operator step','Continues an existing machine task.'),
'samcnpc:run_prepare_field_task':('Field preparation step','Continues an existing field-preparation task.'),
'samcnpc:run_planting_task':('Tree planting step','Continues an existing planting task.'),
'samcnpc:run_farm_task':('Farmer task step','Continues an existing farming task.'),
'samcnpc:run_lumberjack_task':('Lumberjack task step','Continues an existing lumberjack task.'),
'samcnpc:run_lumberjack_demo':('Lumberjack demo step','Continues the existing demo job started by /samcnpc behavior lumberjack <NPC>.'),
},
'de': {
'samcnpc:always':('Immer','Bedingung, die immer wahr ist.'),
'samcnpc:has_summoner':('Hat Beschwörer','Der NPC hat eine gebundene Beschwörer-UUID. Das bedeutet nicht, dass der Spieler gerade sichtbar ist.'),
'samcnpc:summoner_online':('Beschwörer verfügbar','Der Beschwörer ist ein lebender Spieler in der begrenzten Behavior-Beobachtung.'),
'samcnpc:distance_to_summoner':('Abstand zum Beschwörer','Vergleicht den horizontalen Abstand zum beobachteten Beschwörer.'),
'samcnpc:has_unhandled_damage':('Neuer Schaden','Neues Schadensereignis, das noch nicht von der Reaktionslogik verarbeitet wurde.'),
'samcnpc:has_attack_target':('Hat Kampfziel','Behavior hält ein lebendes Kampfziel; es wird kein neuer Gegner gesucht.'),
'samcnpc:target_alive':('Ziel lebt','Das aktuelle Kampfziel lebt noch.'),
'samcnpc:was_hurt_recently':('Kürzlich verletzt','Prüft das Alter des letzten Schadensereignisses.'),
'samcnpc:health_fraction':('Gesundheitsanteil','Anteil der maximalen Gesundheit; 0,3 entspricht 30 %.'),
'samcnpc:task_ready':('Task bereit','Ein vorhandener Task ist für einen Ausführungsschritt bereit. Erzeugt keinen Task.'),
'samcnpc:task_combat_ready':('Kampfunterbrechung bereit','Der aktuelle Kampf-Task/die Unterbrechung ist bereit.'),
'samcnpc:task_reaction_ready':('Task-Reaktion bereit','Die Richtlinie des vorhandenen Tasks meldet eine bereite Reaktion.'),
'samcnpc:task_inventory_ready':('Task-Logistik bereit','Ein vorhandener Inventar-Task ist bereit.'),
'samcnpc:task_inventory_requested':('Task fordert Logistik','Der vorhandene Task fordert eine Logistik-Unterbrechung an.'),
'samcnpc:look_at_summoner':('Beschwörer ansehen','Dreht den Blick zum beobachteten Beschwörer.'),
'samcnpc:look_at_target':('Ziel ansehen','Dreht den Blick zum aktuellen Kampfziel.'),
'samcnpc:move_to_summoner':('Beschwörer folgen','Navigiert mit Hysterese zum Spieler. Leeres startDistance bedeutet stopDistance + 2.'),
'samcnpc:move_to_target':('Kampfziel annähern','Bewegt sich zum aktuellen Kampfziel; dies ist kein neuer Navigationstask.'),
'samcnpc:stop_movement':('Bewegung stoppen','Gibt die aktuelle Bewegungssteuerung frei.'),
'samcnpc:attack_target':('Ziel angreifen','Nahkampfangriff mit echtem Cooldown, Reichweite und Core-Mechanik.'),
'samcnpc:set_attack_target_from_recent_attacker':('Letzten Angreifer wählen','Wählt einen zulässigen Angreifer aus einem neuen Schadensereignis.'),
'samcnpc:clear_attack_target':('Kampfziel löschen','Löscht das temporäre Behavior-Kampfziel.'),
'samcnpc:begin_task_inventory':('Logistikunterbrechung starten','Setzt eine vorhandene Ausführung fort; erzeugt keine Operation.'),
'samcnpc:run_inventory_task':('Inventar-Task-Schritt','Setzt einen vorhandenen Inventar-Task/eine Unterbrechung fort.'),
'samcnpc:begin_task_reaction':('Task-Reaktion starten','Setzt eine vorhandene Ausführung fort; erzeugt keine Operation.'),
'samcnpc:run_combat_task':('Kampf-Task-Schritt','Setzt einen vorhandenen Kampf-Task/eine Unterbrechung fort.'),
'samcnpc:run_navigation_task':('Navigations-Task-Schritt','Setzt einen vorhandenen Navigationstask fort.'),
'samcnpc:run_delivery_task':('Liefer-/Transport-Schritt','Setzt einen vorhandenen Liefer-/Transporttask fort.'),
'samcnpc:run_mining_task':('Bergbau-Task-Schritt','Setzt einen vorhandenen Bergbautask fort.'),
'samcnpc:run_food_task':('Nahrungs-Task-Schritt','Setzt einen vorhandenen Nahrungssammel-Task fort.'),
'samcnpc:run_explorer_task':('Erkundungs-Task-Schritt','Setzt einen vorhandenen Erkundungstask fort.'),
'samcnpc:run_fishing_task':('Angel-Task-Schritt','Setzt einen vorhandenen Angeltask fort.'),
'samcnpc:run_machine_task':('Maschinen-Task-Schritt','Setzt einen vorhandenen Maschinentask fort.'),
'samcnpc:run_prepare_field_task':('Feldvorbereitungs-Schritt','Setzt einen vorhandenen Feldvorbereitungs-Task fort.'),
'samcnpc:run_planting_task':('Pflanz-Task-Schritt','Setzt einen vorhandenen Pflanz-Task fort.'),
'samcnpc:run_farm_task':('Farm-Task-Schritt','Setzt einen vorhandenen Farmtask fort.'),
'samcnpc:run_lumberjack_task':('Holzfäller-Task-Schritt','Setzt einen vorhandenen Holzfäller-Task fort.'),
'samcnpc:run_lumberjack_demo':('Holzfäller-Demo-Schritt','Setzt den Demo-Job fort, der mit /samcnpc behavior lumberjack <NPC> gestartet wurde.'),
}}

ARG_LABELS = {
'en': {'Porównanie':'Comparison','Dystans [bloki]':'Distance [blocks]','Ostatnie N ticków':'Last N ticks','Ułamek zdrowia':'Health fraction','Prędkość (powyżej 1: sprint)':'Speed (>1 requests sprint)','Dystans zatrzymania':'Stop distance','Dystans wznowienia':'Resume distance','Zasięg pościgu':'Chase leash','Limit pościgu [ticki]':'Chase limit [ticks]','Dopuść graczy (nie włączać pochopnie)':'Allow players (use carefully)'},
'de': {'Porównanie':'Vergleich','Dystans [bloki]':'Abstand [Blöcke]','Ostatnie N ticków':'Letzte N Ticks','Ułamek zdrowia':'Gesundheitsanteil','Prędkość (powyżej 1: sprint)':'Geschwindigkeit (>1 fordert Sprint an)','Dystans zatrzymania':'Stoppabstand','Dystans wznowienia':'Wiederaufnahme-Abstand','Zasięg pościgu':'Verfolgungsradius','Limit pościgu [ticki]':'Verfolgungslimit [Ticks]','Dopuść graczy (nie włączać pochopnie)':'Spieler zulassen (vorsichtig verwenden)'},
}

def tr(lang: str, key: str, **fmt) -> str:
    lang = lang if lang in STRINGS else DEFAULT_LANGUAGE
    value = STRINGS[lang].get(key, STRINGS[DEFAULT_LANGUAGE].get(key, key))
    return value.format(**fmt) if fmt else value

def example_label(lang: str, internal_name: str) -> str:
    return EXAMPLE_LABELS.get(internal_name, {}).get(lang, EXAMPLE_LABELS.get(internal_name, {}).get(DEFAULT_LANGUAGE, internal_name))

def localized_meta(lang: str, meta: dict) -> dict:
    if not meta:
        return meta
    out = dict(meta)
    pair = CATALOG.get(lang, {}).get(meta.get('id'))
    if pair:
        out['label'], out['description'] = pair
    args = {}
    for name, spec in meta.get('args', {}).items():
        clone = dict(spec)
        clone['label'] = ARG_LABELS.get(lang, {}).get(spec.get('label'), spec.get('label', name))
        args[name] = clone
    out['args'] = args
    return out

# Shown only if an unexpected Tk callback fails; do not silently close the editor.
STRINGS['en'].update({
    'callback_error': 'An interface action failed. The editor is still open; check your last edit before saving.\nError details: {path}',
    'error_log_console': 'Console (the log file could not be written)',
})
STRINGS['pl'].update({
    'callback_error': 'Wystąpił błąd interfejsu. Edytor pozostaje otwarty; przed zapisem sprawdź ostatnią zmianę.\nSzczegóły błędu: {path}',
    'error_log_console': 'Konsola (nie udało się zapisać pliku logu)',
})
STRINGS['de'].update({
    'callback_error': 'Bei einer Oberflächenaktion ist ein Fehler aufgetreten. Der Editor bleibt geöffnet; prüfe die letzte Änderung vor dem Speichern.\nFehlerdetails: {path}',
    'error_log_console': 'Konsole (die Protokolldatei konnte nicht geschrieben werden)',
})

for language, values in {
    'en': {'refresh_catalog':'Load registered catalog…','install_zip':'Install current ZIP…','text_length':'Item query · 1..{maximum} characters','catalog_loaded':'Catalog {version}: {conditions} conditions, {actions} actions.','install_title':'Install JSON or ZIP into a Minecraft instance','offline_snapshot':'registered catalog · v2','about_version':'Behavior Studio 1.3.0 · registered catalog 2'},
    'pl': {'refresh_catalog':'Wczytaj zarejestrowany katalog…','install_zip':'Instaluj bieżący ZIP…','text_length':'Zapytanie o przedmiot · 1..{maximum} znaków','catalog_loaded':'Katalog {version}: {conditions} warunków, {actions} akcji.','install_title':'Instalacja JSON lub ZIP w instancji Minecraft','offline_snapshot':'zarejestrowany katalog · v2','about_version':'Behavior Studio 1.3.0 · zarejestrowany katalog 2'},
    'de': {'refresh_catalog':'Registrierten Katalog laden…','install_zip':'Aktuelles ZIP installieren…','text_length':'Gegenstandsabfrage · 1..{maximum} Zeichen','catalog_loaded':'Katalog {version}: {conditions} Bedingungen, {actions} Aktionen.','install_title':'JSON oder ZIP in einer Minecraft-Instanz installieren','offline_snapshot':'registrierter Katalog · v2','about_version':'Behavior Studio 1.3.0 · registrierter Katalog 2'},
}.items(): STRINGS[language].update(values)

_LOCAL_COMPONENTS = {
    'inventory_count': (
        ('Inventory count','Count exact items or a declared role. Main hand is counted once. minecraft:coal excludes charcoal.'),
        ('Liczba przedmiotów','Zlicza dokładny przedmiot lub jawną rolę. Główna ręka liczona jest raz. minecraft:coal wyklucza węgiel drzewny.'),
        ('Anzahl im Inventar','Exakte Gegenstände oder eine angegebene Rolle zählen. Haupthand zählt einmal. minecraft:coal schließt Holzkohle aus.')),
    'inventory_free_slots': (
        ('Free inventory slots','Compare empty carried slots. Partly filled stacks are not empty slots.'),
        ('Wolne miejsca','Porównuje puste miejsca w ekwipunku. Częściowo wypełniony stos nie jest pustym miejscem.'),
        ('Freie Inventarplätze','Leere Inventarplätze vergleichen. Teilweise gefüllte Stapel sind keine leeren Plätze.')),
    'equipment_matches': (
        ('Equipment matches','Check one equipment destination against a query and minimum remaining durability.'),
        ('Wyposażenie pasuje','Sprawdza wskazane miejsce wyposażenia według zapytania i minimalnej pozostałej trwałości.'),
        ('Ausrüstung passt','Einen Ausrüstungsplatz nach Abfrage und minimaler Resthaltbarkeit prüfen.')),
    'durability_fraction': (
        ('Remaining durability','Compare remaining durability from 0 to 1. Empty equipment never matches.'),
        ('Pozostała trwałość','Porównuje pozostałą trwałość od 0 do 1. Puste wyposażenie nie spełnia warunku.'),
        ('Resthaltbarkeit','Resthaltbarkeit von 0 bis 1 vergleichen. Ein leerer Platz erfüllt die Bedingung nicht.')),
    'at_position': (
        ('At position','Compare the NPC feet position with a bounded three-dimensional radius.'),
        ('Na pozycji','Porównuje pozycję stóp NPC z punktem i ograniczonym promieniem w trzech wymiarach.'),
        ('An Position','Die Fußposition des NPC mit einem Punkt und begrenztem räumlichem Radius vergleichen.')),
    'task_status': (
        ('Task status','Check the existing durable task. With no task, this condition is false.'),
        ('Stan zadania','Sprawdza istniejące trwałe zadanie. Bez zadania warunek jest fałszywy.'),
        ('Task-Status','Den bestehenden dauerhaften Task prüfen. Ohne Task ist die Bedingung falsch.')),
    'task_attempts_remaining': (
        ('Attempts remaining','Compare remaining attempts in the active durable task frame.'),
        ('Pozostałe próby','Porównuje liczbę pozostałych prób w aktywnej ramce trwałego zadania.'),
        ('Verbleibende Versuche','Verbleibende Versuche im aktiven dauerhaften Task vergleichen.')),
    'last_task_failure': (
        ('Last task failure','Match a recorded failure reason; absence of a failure is not a match.'),
        ('Ostatni błąd zadania','Dopasowuje zapisany powód błędu. Brak błędu nie spełnia warunku.'),
        ('Letzter Task-Fehler','Einen aufgezeichneten Fehlergrund prüfen; ohne Fehler keine Übereinstimmung.')),
    'container_observed': (
        ('Container observed','Only an authorized endpoint of the current task or logistics policy. Unknown is not empty.'),
        ('Skrzynia zaobserwowana','Tylko dozwolony punkt bieżącego zadania lub polityki logistyki. Nieznana zawartość nie oznacza pustej.'),
        ('Behälter beobachtet','Nur ein erlaubter Endpunkt des aktuellen Tasks oder der Logistikrichtlinie. Unbekannt bedeutet nicht leer.')),
    'container_count': (
        ('Container item count','Count a query at an authorized SOURCE or DESTINATION index. Unknown observations never satisfy a numeric comparison.'),
        ('Liczba w skrzyni','Zlicza zapytanie we wskazanym dozwolonym SOURCE lub DESTINATION. Nieznany stan nie spełnia porównania liczbowego.'),
        ('Anzahl im Behälter','Eine Abfrage am erlaubten SOURCE- oder DESTINATION-Index zählen. Unbekannte Beobachtungen erfüllen keinen Zahlenvergleich.')),
    'container_free_slots': (
        ('Free container slots','Empty slots in an authorized observed chest; this does not guarantee NBT-compatible stacking.'),
        ('Wolne miejsca w skrzyni','Puste miejsca dozwolonej zaobserwowanej skrzyni; nie gwarantuje zgodności NBT przy łączeniu stosów.'),
        ('Freie Behälterplätze','Leere Plätze einer erlaubten beobachteten Truhe; keine Garantie für NBT-kompatibles Stapeln.')),
    'ensure_equipment': (
        ('Ensure equipment','Keep suitable equipment or equip a deterministic carried match. Chest collection belongs to the durable ENSURE operation or preparation policy.'),
        ('Zapewnij wyposażenie','Zachowuje właściwe wyposażenie lub zakłada deterministycznie wybrany przedmiot z ekwipunku. Pobranie ze skrzyni należy do trwałej operacji ENSURE lub polityki przygotowania.'),
        ('Ausrüstung sicherstellen','Geeignete Ausrüstung behalten oder einen passenden getragenen Gegenstand deterministisch anlegen. Truhenentnahme gehört zur dauerhaften ENSURE-Operation oder Vorbereitung.')),
}
EXAMPLE_LABELS['Tool preparation']={'en':'Tool preparation — inventory query','pl':'Przygotowanie narzędzia — ekwipunek','de':'Werkzeugvorbereitung — Inventarabfrage'}
for identifier, translations in _LOCAL_COMPONENTS.items():
    for language, pair in zip(('en','pl','de'),translations): CATALOG.setdefault(language,{})['samcnpc:'+identifier]=pair

for language, labels in {
    'en': {'query':'Item query','operator':'Comparison','count':'Count','destination':'Equipment destination','minimumDurability':'Minimum durability (0..1)','endpoint':'Permitted endpoint','index':'Endpoint index','value':'Fraction','status':'Task status','reason':'Failure reason','radius':'Radius','x':'X','y':'Y','z':'Z'},
    'pl': {'query':'Zapytanie o przedmiot','operator':'Porównanie','count':'Liczba','destination':'Miejsce wyposażenia','minimumDurability':'Minimalna trwałość (0..1)','endpoint':'Dozwolony punkt','index':'Indeks punktu','value':'Ułamek','status':'Stan zadania','reason':'Powód błędu','radius':'Promień','x':'X','y':'Y','z':'Z'},
    'de': {'query':'Gegenstandsabfrage','operator':'Vergleich','count':'Anzahl','destination':'Ausrüstungsplatz','minimumDurability':'Mindesthaltbarkeit (0..1)','endpoint':'Erlaubter Endpunkt','index':'Endpunktindex','value':'Anteil','status':'Task-Status','reason':'Fehlergrund','radius':'Radius','x':'X','y':'Y','z':'Z'},
}.items(): ARG_LABELS.setdefault(language,{}).update(labels)
