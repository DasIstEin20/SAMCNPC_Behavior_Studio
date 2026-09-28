> Historical 1.1.1 reference. Current 1.2.0 uses the bundled registered catalog (25 conditions / 25 actions). See README and TEST_REPORT for current behavior and validation.

# Katalog obsługiwanych komponentów

Snapshot: `b92ec0e23164f822f450fc65a006ce9039cec37a`.

## 17 paczek wbudowanych

- `samcnpc:idle_look`
- `samcnpc:follow_summoner`
- `samcnpc:retaliate`
- `samcnpc:demo_lumberjack`
- `samcnpc:task_navigation`
- `samcnpc:task_delivery`
- `samcnpc:task_lumberjack`
- `samcnpc:task_mining`
- `samcnpc:task_food`
- `samcnpc:task_farming`
- `samcnpc:task_prepare_field`
- `samcnpc:task_planting`
- `samcnpc:task_machine`
- `samcnpc:task_fishing`
- `samcnpc:task_explorer`
- `samcnpc:task_combat`
- `samcnpc:task_inventory`

## Warunki (14)

### `samcnpc:always` — Zawsze

Warunek zawsze prawdziwy.

Argumenty: brak.


### `samcnpc:has_summoner` — Ma przywołującego

NPC ma przypisany UUID summonnera. To nie znaczy, że gracz jest dostępny.

Argumenty: brak.


### `samcnpc:summoner_online` — Przywołujący dostępny

Przywołujący jest żywym graczem dostępnym w ograniczonej obserwacji Behavior.

Argumenty: brak.


### `samcnpc:distance_to_summoner` — Dystans do przywołującego

Porównuje poziomy dystans do obserwowanego summonnera.

- `operator`: string, wymagane, gt | gte | lt | lte | eq.
- `blocks`: number, wymagane, 0..256.

### `samcnpc:has_unhandled_damage` — Nowe obrażenia

Nowe, jeszcze nieobsłużone zdarzenie obrażeń; pamięć reakcji ogranicza jego wiek.

Argumenty: brak.


### `samcnpc:has_attack_target` — Ma cel walki

Behavior ma żywy cel walki; nie wyszukuje nowego przeciwnika.

Argumenty: brak.


### `samcnpc:target_alive` — Cel jest żywy

Aktualny cel walki nadal jest żywy.

Argumenty: brak.


### `samcnpc:was_hurt_recently` — Niedawno zraniony

Sprawdza wiek ostatniego zdarzenia obrażeń.

- `withinTicks`: integer, wymagane, 1..120000.

### `samcnpc:health_fraction` — Poziom zdrowia

Ułamek maksymalnego zdrowia: 0.3 oznacza 30%.

- `operator`: string, wymagane, gt | gte | lt | lte | eq.
- `value`: number, wymagane, 0..1.

### `samcnpc:task_ready` — Zadanie gotowe

Istniejący task jest gotowy do kroku wykonania. Nie tworzy taska ani nie sprawdza jego typu.

Argumenty: brak.


### `samcnpc:task_combat_ready` — Przerwanie walką gotowe

Gotowy jest aktualny task walki/przerwanie.

Argumenty: brak.


### `samcnpc:task_reaction_ready` — Reakcja zadania gotowa

Polityka istniejącego taska zgłasza gotową reakcję.

Argumenty: brak.


### `samcnpc:task_inventory_ready` — Logistyka zadania gotowa

Gotowe jest istniejące zadanie pracy z ekwipunkiem.

Argumenty: brak.


### `samcnpc:task_inventory_requested` — Zadanie żąda logistyki

Istniejący task zgłasza potrzebę logistycznego przerwania.

Argumenty: brak.



## Akcje (24)

### `samcnpc:look_at_summoner` — Patrz na przywołującego

Obraca widok w stronę obserwowanego gracza.

Kanały: `look`.

Argumenty: brak.


### `samcnpc:look_at_target` — Patrz na cel

Obraca widok w stronę aktualnego celu walki.

Kanały: `look`.

Argumenty: brak.


### `samcnpc:move_to_summoner` — Podążaj za przywołującym

Nawigacja do gracza z histerezą. Puste startDistance oznacza stopDistance + 2. Musi być większe od stopDistance.

Kanały: `movement`, `look`.

- `speed`: number, wymagane, 0.1..1.5.
- `stopDistance`: number, wymagane, 0..16.
- `startDistance`: number, opcjonalne, 0.25..32; pominięte: stopDistance + 2; obowiązuje start > stop.

### `samcnpc:move_to_target` — Podejdź do celu walki

Steruje ruchem w stronę aktualnego celu walki; nie jest nowym taskiem nawigacji.

Kanały: `movement`, `look`.

- `speed`: number, wymagane, 0.1..1.5.
- `stopDistance`: number, wymagane, 0..16.

### `samcnpc:stop_movement` — Zatrzymaj ruch

Zwalnia bieżące sterowanie ruchem.

Kanały: `movement`.

Argumenty: brak.


### `samcnpc:attack_target` — Uderz cel

Melee w aktualny cel; sprawdza rzeczywisty cooldown, zasięg i mechanikę Core.

Kanały: `combat`, `main_hand`.

Argumenty: brak.


### `samcnpc:set_attack_target_from_recent_attacker` — Ustaw ostatniego napastnika

Wybiera kwalifikującego się napastnika z nowego zdarzenia obrażeń. Nie wyszukuje najbliższego wroga.

Kanały: `combat`.

- `leash`: number, opcjonalne, 1..32; domyślnie 24.
- `durationTicks`: integer, opcjonalne, 20..2400; domyślnie 600.
- `allowPlayers`: boolean, opcjonalne, true / false; domyślnie false.

### `samcnpc:clear_attack_target` — Wyczyść cel walki

Czyści przejściowy cel Behavior.

Kanały: `combat`.

Argumenty: brak.


### `samcnpc:begin_task_inventory` — Rozpocznij przerwanie logistyką

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: istniejący task + polityka logistyki.

Kanały: `movement`, `look`, `main_hand`, `off_hand`, `combat`, `interaction`, `block_action`, `inventory`.

Argumenty: brak.


### `samcnpc:run_inventory_task` — Krok pracy ekwipunku

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_inventory (lub przerwanie taska).

Kanały: `movement`, `look`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:begin_task_reaction` — Rozpocznij reakcję taska

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: istniejący task + polityka reakcji.

Kanały: `combat`.

Argumenty: brak.


### `samcnpc:run_combat_task` — Krok walki taska

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_combat (lub przerwanie taska).

Kanały: `movement`, `look`, `combat`, `main_hand`, `off_hand`, `inventory`.

Argumenty: brak.


### `samcnpc:run_navigation_task` — Krok nawigacji

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_navigation.

Kanały: `movement`, `look`.

Argumenty: brak.


### `samcnpc:run_delivery_task` — Krok dostawy / transportu

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_delivery.

Kanały: `movement`, `look`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_mining_task` — Krok minera

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_mining.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_food_task` — Krok pozyskiwania żywności

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_food.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_explorer_task` — Krok eksploratora

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_explorer.

Kanały: `movement`, `look`.

Argumenty: brak.


### `samcnpc:run_fishing_task` — Krok łowienia

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_fishing.

Kanały: `movement`, `look`, `main_hand`, `off_hand`, `combat`, `interaction`, `block_action`, `inventory`.

Argumenty: brak.


### `samcnpc:run_machine_task` — Krok operatora maszyny

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_machine.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_prepare_field_task` — Krok przygotowania poletka

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_prepare_field.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_planting_task` — Krok sadzenia drzew

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_planting.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_farm_task` — Krok farmera

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_farming.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_lumberjack_task` — Krok drwala

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: samcnpc:task_lumberjack.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.


### `samcnpc:run_lumberjack_demo` — Krok demo drwala

Kontynuuje istniejące wykonanie. Nie uruchamia operacji i nie przyjmuje jej parametrów. Wymaga: aktywny job /samcnpc behavior lumberjack <NPC>.

Kanały: `movement`, `look`, `main_hand`, `block_action`, `inventory`, `interaction`.

Argumenty: brak.
