# Strażnik–robotnik: zaawansowana autonomia NPC

Otwórz **guardian_forester.samgraph** w Behavior Studio 1.3.0 (Plik → Otwórz).
W lewym panelu „Reguły w paczce” wybierz interesującą regułę, aby szybko do niej przejść.
Projekt zawiera **33 reguły, 506 węzłów i 473 połączenia**, w sześciu obszarach.
Powiększaj kółkiem, przesuwaj płótno środkowym przyciskiem myszy. Wybór reguły pokazuje
jej priorytet i parametry; identyfikatory a01…f03 opisują konkretne decyzje.

## Co robi NPC

| Obszar | Zachowanie |
| --- | --- |
| 01 SAFETY | Szanuje ręczną pauzę; przy krytycznym zdrowiu przerywa odwet i wraca do widocznego summonera albo zatrzymuje się. |
| 02 DEFENSE | Odpowiada na własny świeży atak, dobiera noszoną broń i tarczę, podchodzi i walczy. Bez odpowiedniej broni zrywa odwet. |
| 03 DURABLE TASKS | Kontynuuje autoryzowane reakcje, patrol i logistykę. Rozróżnia pełny ekwipunek, brak siekiery, widoczny zapas i nieznaną skrzynię. |
| 04 EQUIPMENT | W spokoju zakłada cztery elementy pancerza i tarczę; przygotowuje siekierę i wymienia zużytą na noszony zapas. |
| 05 RESULTS | Po ukończeniu lub wybranych porażkach wraca do summonera. W czasie przerwy przed ponowną próbą czeka. |
| 06 ESCORT | Eskortuje summonera; przy odległości ponad 12 bloków prosi o zwykły sprint. Bez summonera pozostaje w miejscu. |

Bez zadania działają eskorta, odwet i wyposażenie. Praca, patrol, pobranie ze skrzyni
oraz rozładunek wymagają przypisania trwałego zadania i jego uprawnień.

## Instalacja paczki

Skopiuj **guardian_forester.zip**, bez wypakowywania, do:

`%APPDATA%\.minecraft\resources\samcnpc\behaviors\`

Archiwum zawiera `behaviors/showcase_guardian_forester.json` oraz instrukcje instalacji.
Alternatywnie sam JSON można umieścić w `config/samcnpc/behaviors/`.
**Wybierz jeden format**: jednoczesny JSON i ZIP z tym samym ID spowodują odrzucenie reloadu.
Plik `.samgraph` służy do edycji i nie jest instalowany do Minecrafta.

Na bezczynnym NPC o nazwie Sam:

```text
/samcnpc behavior reload
/samcnpc behavior assign Sam showcase:guardian_forester
/samcnpc behavior diagnostics Sam
```

Daj mu fizycznie wyposażenie: miecz lub siekierę, zapasową siekierę, tarczę i pancerz.
Graf nie generuje przedmiotów. Samo założenie tarczy nie oznacza podniesienia jej do bloku.
To profil reaktywny, bez wyszukiwania i atakowania wszystkich pobliskich stworzeń.

## Pełny pokaz: narzędzie → drewno → rozładunek

Przykładowa arena na Y=64: NPC i summoner przy (0,64,0), skrzynia narzędzi
(3,64,3), skrzynia nadmiarowych przedmiotów (3,64,-3), skrzynia drewna (16,64,0).
W obszarze od (6,64,-2) do (10,70,2) umieść co najmniej 8 kłód dębu.
Zapewnij grunt i przejścia. W narzędziowej umieść siekierę oraz inne narzędzia;
puste skrzynie muszą być odblokowane. Zmień współrzędne, jeśli twoja arena jest gdzie indziej.

Na bezczynnym NPC wykonaj kolejno:

```text
/samcnpc behavior task assign Sam lumberjack 6 64 -2 10 70 2 16 64 0 samcnpc:oak 8 12000
/samcnpc behavior task pause Sam
/samcnpc behavior task logistics Sam prepare "@axe" 1 "3,64,3" MAIN_HAND 0.25 0
/samcnpc behavior task logistics Sam free_slots "3,64,-3" "minecraft:cobblestone=64" 2
/samcnpc behavior task reaction Sam retaliate 12 240 false
/samcnpc behavior task tactics Sam auto
/samcnpc behavior task tactics Sam retreat 0.35 0.60
/samcnpc behavior assign Sam samcnpc:task_lumberjack,showcase:guardian_forester
/samcnpc behavior task resume Sam
/samcnpc behavior task status Sam
/samcnpc behavior task inventory_history Sam 1
```

`task assign` najpierw ustanawia kontroler zadania. Dopiero później dołącz graf,
zachowując **samcnpc:task_lumberjack**. Zwykłe `behavior assign` zastępuje CAŁĄ listę;
usunięcie kontrolera z aktywnego zadania może je anulować. Krótka pauza pozwala ustawić
politykę przed dalszą pracą; nie cofa efektów wykonanych przed pauzą.

Przy braku siekiery trwałe przygotowanie idzie do dozwolonej skrzyni, zabiera użyteczną
siekierę, zakłada ją i weryfikuje rezultat. Rozładunek wolno wykonać tylko dla nadmiaru
brukowca ponad rezerwę 64; drewno zadania i wyposażenie pozostają chronione. Aby pokazać
rozładunek, wypełnij uprzednio 35 slotów NPC brukowcem. Po dostarczeniu 8 kłód NPC wraca
do summonera. Porażka ma skończony budżet i jawny wynik; graf nie odnawia go w pętli.

W czasie zadania sprzętem bojowym, leczeniem i odwrotem zarządza skonfigurowany
kontroler walki. Reguły swobodnego odwetu i przygotowania pancerza dotyczą bezczynności,
więc nie przełączają robotnikowi broni podczas ścinania ani obsługi skrzyni.

## Patrol z ochroną summonera

Na bezczynnym NPC przy (0,64,0), na równej dostępnej trasie:

```text
/samcnpc behavior task assign Sam patrol 24 3 40 6000 "0.5,64,0.5;8.5,64,0.5;8.5,64,8.5;0.5,64,8.5" protect_summoner false
/samcnpc behavior task tactics Sam auto
/samcnpc behavior assign Sam samcnpc:task_combat,showcase:guardian_forester
```

To skończone trzy okrążenia z postojami, reakcją na napastnika summonera i powrotem.
Nie uruchamiaj patrolu równocześnie z aktywnym zadaniem drewna: jeden NPC ma jedno zadanie
podstawowe. Graf nie tworzy automatycznie następnej misji po zakończeniu obecnej.

## Granice i strojenie

- Krytyczne zdrowie w trybie swobodnym: ≤25%; przy świeżym urazie/celu próg ostrożności wynosi ≤40%. Atak jest dozwolony dopiero powyżej 40%.
- Odwet dotyczy wyłącznie świeżego napastnika: promień 12 bloków, 240 ticków, bez graczy. Te limity egzekwuje istniejący mechanizm Behavior.
- Siekiera zapasowa: minimum 25% trwałości; pancerz i tarcza: 20%; broń do odwetu: 10%.
- Śledzenie: start 5 bloków, stop 3 bloki. Ta różnica zapobiega ciągłemu przełączaniu ruchu.
- Priorytet reguły jest porównywany przed priorytetem paczki. Akcja wymagająca kilku kanałów musi uzyskać wszystkie. Nie zakładaj kolejności wykonywania niezależnych akcji.
- `minecraft:coal` jest dokładnym przedmiotem. Węgiel drzewny nie spełnia tego warunku. Reguła c06 kontynuuje istniejące zadanie ekwipunku, nie ustanawia nowego żądania węgla.
- Reguły c03–c09 nazywają rozpoznaną sytuację w diagnostyce. Kierunek i zakres transferu nadal wynikają z kontraktu zadania; reguła nie może zmienić go samą obserwacją.
- Nieznana skrzynia nie jest pusta. c08 pozwala kontrolerowi podejść i ją obejrzeć; c10 obsługuje pozostałe etapy, częściowe stosy, powrót i weryfikację.
- Kontroler podstawowej pracy pozostaje we wbudowanej paczce. Graf może współpracować z innymi zadaniami, gdy zachowasz ich właściwy kontroler.
- Sam JSON/ZIP nie dodaje algorytmów Kotlin, craftingów, komend, skryptów, globalnego dostępu do skrzyń ani ukrytych wywołań LLM.
- Swobodny odwrót nie używa jedzenia i nie obiecuje samoleczenia. Przy braku summonera NPC stoi; nie wyznacza magicznie bezpiecznej lokalizacji.

## Sprawdzenie w grze

1. Daj zużytą i nową siekierę: nowa powinna trafić do ręki, stara pozostać w ekwipunku.
2. Daj pancerz i tarczę: w spokoju powinny zostać założone bez tworzenia zadania.
3. Sprowokuj pojedynczy atak moba przy dobrym zdrowiu, potem obniż zdrowie NPC w kopii świata testowego: odwet ma się zakończyć.
4. Wykonaj pokaz drewna i porównaj fizyczną zawartość trzech skrzyń oraz raport zadania.
5. Użyj pauzy: zadanie nie ma być wznawiane przez graf. Wznów jawnie.
6. Odsuń NPC od skrzyni: brak obserwacji nie powinien zmienić się w raport „zero przedmiotów”.

`build_showcase.py` odtwarza projekt i eksporty z katalogu Studio; nie wchodzi do instalowanej paczki.
