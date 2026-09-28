> Historical 1.1.1 reference. Current 1.2.0 uses the bundled registered catalog (25 conditions / 25 actions). See README and TEST_REPORT for current behavior and validation.

# Audyt formatu paczek i ładowania

Repo: `DasIstEin20/SAMCNPC_Behavior`.
Sprawdzony `main`: `b92ec0e23164f822f450fc65a006ce9039cec37a` (commit z 23.09.2026).
Kreator celuje w ten snapshot; nie śledzi sam przyszłych aktualizacji.

## Dane źródłowe

Wszystkie odnośniki poniżej wskazują na ten sam, zamrożony commit:

- [BehaviorPackLoader.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/registry/BehaviorPackLoader.kt)
  — 17 wymienionych z nazwy zasobów wbudowanych, odczyt classloaderem,
  dodatkowo `BehaviorPackFiles.readExternal(FMLPaths.CONFIGDIR.get())`;
  odrzucanie duplikatów ID; rejestr jest podmieniany dopiero po kompilacji całości.
- [BehaviorPackFiles.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/registry/BehaviorPackFiles.kt)
  — `config/samcnpc/behaviors`, `Files.list` (bez rekursji), sufiks `.json`,
  64 JSON-y / 1024 wpisy, sprawdzanie zwykłych plików, dowiązań i stabilności odczytu.
- [BehaviorPackCompiler.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/registry/BehaviorPackCompiler.kt)
  — schemaVersion 1, pola paczki/reguły, test/all/any/not, zarejestrowane ID,
  kanały akcji, głębokość 8, limit 256 reguł i 16 akcji.
- [BoundedBehaviorJson.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/registry/BoundedBehaviorJson.kt)
  — 128 KiB, 32 poziomy JSON, 16384 wartości, teksty 512 code points,
  tokeny liczb 64 znaki, odrzucanie powtórzonych kluczy i niepoprawnego Unicode.
- [BehaviorDefinitions.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/registry/BehaviorDefinitions.kt)
  — rejestr 14 warunków i 24 akcji wraz z kanałami i walidacją argumentów.
- [FollowMovement.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/runtime/FollowMovement.kt)
  — move_to_summoner: speed 0.1..1.5, stopDistance 0..16,
  opcjonalne startDistance domyślnie stop+2, zakres 0.25..32 i start > stop.
- [BehaviorTargetMemory.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/runtime/BehaviorTargetMemory.kt)
  — set_attack_target_from_recent_attacker: opcjonalne leash 1..32,
  durationTicks 20..2400 i allowPlayers; domyślnie 24 / 600 / false.
- [BehaviorDecisionPlan.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/runtime/BehaviorDecisionPlan.kt)
  i [BehaviorArbiter.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/model/BehaviorArbiter.kt)
  — warunki ocenia się przed wykonaniem; akcje są kandydatami, nie workflow;
  konflikt dowolnego kanału wyklucza całą kandydaturę; cooldown po ACCEPTED/SUCCEEDED.
- [TaskService.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/task/TaskService.kt)
  — stałe pack/action; executeSelected wymaga istniejącego pasującego taska;
  assignmentsChanged anuluje task po usunięciu jego oryginalnego pack ID.
- [LumberjackService.kt](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/kotlin/io/samcnpc/behavior/lumberjack/LumberjackService.kt)
  — `start` tworzy stan, szuka skrzyni w 50×50 i przypisuje demo pack;
  samo wywołanie registered run_lumberjack_demo jest kontynuacją, nie `start`.
- [demo_lumberjack.json](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/resources/data/samcnpc_behavior/behaviors/demo_lumberjack.json)
  i [task_lumberjack.json](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/src/main/resources/data/samcnpc_behavior/behaviors/task_lumberjack.json)
  — referencje grafów w kreatorze zachowują reguły, akcje i priorytety;
  opisy w szablonach są wyraźnie oznaczone jako referencyjne.
- [BEHAVIOR_AUTHORING.md](https://github.com/DasIstEin20/SAMCNPC_Behavior/blob/b92ec0e23164f822f450fc65a006ce9039cec37a/docs/BEHAVIOR_AUTHORING.md)
  — oficjalna dla projektu instrukcja pliku config, reload, packs, assign, diagnostics;
  walidacja niezależnym schematem nie zastępuje kompilatora/loadera.

## Odpowiedź o „resources”

Nie ma automatycznego ładowania nowych behavior JSON-ów z client resource packów,
server datapacków ani dowolnych ZIP-ów. Nie ma ogólnego odkrywania wszystkich zasobów
`data/*/behaviors/*.json` przez ResourceManager w zbadanym loaderze.

Jest ścieżka classpath do konkretnych wbudowanych plików i pomocniczy fallback
ForgeGradle do tych samych konkretnych nazw w katalogu gry. Ten fallback nie jest
nowym formatem paczki ani skanerem folderu resources.

Dla custom packów obecnie właściwy jest płaski katalog config. Dodanie wsparcia
datapacków wymaga pracy po stronie Behavior. Nie trzeba do tego tworzyć nowego JAR-a
ani zmieniać Core/LLM, ale trzeba zaprojektować źródła, priorytety, reload i konflikty.

## Zakres edytora

Katalog GUI został odtworzony z rzeczywistych rejestracji, a nie z wyobrażonego API.
Nie dodano węzłów typu has_axe, generic mine(pos), craft ani dowolnej sekwencji.
Zaawansowane mosty tasków pozostają dostępne do analizy, ale mają ostrzeżenia.
Import wbudowanego ID jest dozwolony do oglądania; instalacja/eksport do config z takim
ID jest blokowana, bo byłby to duplikat, nie override.
