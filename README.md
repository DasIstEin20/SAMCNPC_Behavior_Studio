<p align="center">
  <img src="assets/samcnpc_behavior_studio_logo.png" width="720" alt="SAMCNPC Behavior Studio" />
</p>

# SAMCNPC Behavior Studio

English | [Polski](README_PL.md) | [Deutsch](README_DE.md)

**An offline visual editor for deterministic NPC behavior packs — SAMCNPC on Minecraft Forge 1.20.1.**

Build rules by connecting conditions and actions, inspect the generated JSON, validate your graph,
and install the resulting behavior pack in your Minecraft instance. Studio 1.2.0 includes a dark
node editor, an English/Polish/German interface, working examples and three illustrated GitHub guides.
You do not need to write code to edit a pack.

[SAMCNPC Core](https://github.com/DasIstEin20/SAMCNPC_Core) provides the NPC's body and mechanics.
[SAMCNPC Behavior](https://github.com/DasIstEin20/SAMCNPC_Behavior) executes the rules and durable tasks.
Studio authors their data; it runs independently of Minecraft and does not require an LLM,
API keys, a cloud service or additional Python packages.

[Get started](#getting-started) · [Tutorials](#tutorials) ·
[Examples](#examples) · [Install a pack](#export-and-installation) · [Validation](#validation)

## Features

- **Visual rules:** conditions, `all` / `any` / `not` groups, actions, rule priorities,
  cooldowns and explicit action channels in a dark node editor.
- **Editable projects:** save `.samgraph` projects, open existing format-1 projects,
  import behavior JSON, undo edits and inspect a live JSON preview.
- **Catalog-driven controls:** node definitions, fields, bounds, enums, defaults,
  descriptions and channels come from the bundled registered Behavior schema.
  The current catalog has **25 conditions, 25 actions and 17 built-in pack references**.
- **Local autonomy components:** inventory counts and free slots, equipment and durability,
  authorized container observations, position/task/failure facts and `ensure_equipment`.
- **Language switching:** English is the default; switch to Polish or German in the
  existing window while preserving the graph, selection, drafts and undo history.
- **JSON and ZIP workflow:** validate before export, choose the Minecraft instance root,
  then install to the correct directory with duplicate-ID checks and confirmed backup handling.
- **Help and examples:** built-in Help/About, introductory projects, a 506-node advanced
  showcase and illustrated guides in three languages, displayed using your GitHub theme.

A graph describes **conditions → rule → action candidates**. Connections do not form a
step-by-step program: Behavior resolves eligible actions through priorities and channel
arbitration. Durable work, such as collecting a tool from an authorized chest before chopping,
runs in Behavior's existing task system. JSON/ZIP cannot add arbitrary code, commands,
new task algorithms or container permissions.

## Getting started

| Requirement | Details |
| --- | --- |
| Editor | Python **3.10+** with Tkinter/Tcl/Tk and a desktop display |
| Python packages | Standard library only; no `pip install` step |
| Windows launcher | `START_WINDOWS.bat` |
| In-game execution | Matching Core + Behavior builds and Kotlin for Forge, Minecraft Forge **1.20.1** |

Clone the repository using Git, or download and extract its source ZIP:

```powershell
git clone https://github.com/DasIstEin20/SAMCNPC_Behavior_Studio.git
cd SAMCNPC_Behavior_Studio
.\START_WINDOWS.bat
```

You can also run `python studio.py`. On Linux/macOS use `python3 studio.py`;
Tkinter must be installed for that interpreter. The editor does not require Java or Forge.
No Git submodules or neighboring SAMCNPC source repositories are needed.

1. Open `examples/custom/example_follow.samgraph` through **File → Open**.
2. Edit a condition, action or priority, then validate and review the JSON preview.
3. Save your editable `.samgraph` project separately from its exported pack.
4. Export JSON or ZIP and install it as described below.

For gameplay, use a Behavior build compatible with the bundled **registered catalog 2**
and its external ZIP loader. The pack schema/semantics version remains **1**; this does
not mean an older Behavior build knows every new action. Development mod JARs can share
a version number, so check the matching catalog, not just the JAR filename.

## Tutorials

Read the illustrated **Studio 1.2.0** guides directly on GitHub:

| English | Polski | Deutsch |
| --- | --- | --- |
| [Read the guide](tutorials/GUIDE_EN.md) | [Czytaj poradnik](tutorials/GUIDE_PL.md) | [Handbuch lesen](tutorials/GUIDE_DE.md) |

These three Markdown pages replace the six White/Black PDF variants. GitHub applies
your light or dark theme automatically. Each guide preserves the original 20 chapters,
command examples and actual Studio screenshots, with a clickable contents list and
an additional chapter about the advanced Guardian / Forester example.

Learn rule construction, inventory/equipment queries, exact item versus role semantics,
authorized chest observations, safe unloading, priorities/channel conflicts, ZIP installation,
reload and troubleshooting. The practical tool tutorial explains how an NPC obtains
a tool from an allowed chest, equips it and performs work.

The corresponding [tutorial projects](tutorials/examples/) are included, including the
[original Guardian escort graph](tutorials/examples/complex_guardian_escort.samgraph).

## Examples

| Project | What it demonstrates |
| --- | --- |
| [Follow](examples/custom/example_follow.samgraph) | A first movement rule |
| [Cautious follow](examples/custom/example_cautious_follow.samgraph) | Conditional movement and distance |
| [Retaliate](examples/custom/example_retaliate.samgraph) | A bounded response to an attacker |
| [Tool preparation](examples/custom/example_tool_preparation.samgraph) | Equip a usable axe already carried by the NPC |
| [Guardian / Forester](examples/advanced/guardian_forester/guardian_forester.samgraph) | 33 rules, 506 nodes and 473 connections: safety, retaliation, equipment, task recovery and escort |

The advanced example includes [JSON](examples/advanced/guardian_forester/guardian_forester.json),
a directly loadable [ZIP](examples/advanced/guardian_forester/guardian_forester.zip),
a [Polish walkthrough](examples/advanced/guardian_forester/README_PL.md) and
[dated runtime validation](examples/advanced/guardian_forester/VALIDATION.md).
Open it through **File → Open**. Its rules observe and coordinate existing authorized tasks;
assigning the pack alone does not create a work mission or grant access to chests.

![Guardian / Forester in the actual Studio window](examples/advanced/guardian_forester/studio_preview.png)

## Export and installation

Use **Export Behavior Pack JSON** or **Export Behavior Pack ZIP** after validation.
In the Installation tab, select the **Minecraft instance root**; Studio constructs
these directories for you:

| Format | Destination |
| --- | --- |
| JSON | `<instance>/config/samcnpc/behaviors/<name>.json` |
| ZIP | `<instance>/resources/samcnpc/behaviors/<name>.zip` — keep it zipped |

A Studio-generated ZIP contains `behaviors/<name>.json` and installation notes.
It contains no editable project or executable code. This is an external SAMCNPC
resource archive, not a vanilla resource pack or datapack. For multiplayer, install
behavior packs in the **server's** instance.

Keep each pack ID in only one active source: installing both its JSON and ZIP creates
a duplicate. Replacing a file requires confirmation and preserves a backup. Invalid
existing files must be fixed before the complete candidate registry can be accepted.

In Minecraft, after installing the Tool preparation example:

```text
/samcnpc behavior reload
/samcnpc behavior packs
/samcnpc behavior assign Sam example:tool_preparation
/samcnpc behavior diagnostics Sam
```

Replace `Sam` with your NPC's name. Reload requires operator permission; NPC operations
use the normal summoner/operator checks. `assign` replaces the NPC's pack list, so keep
any controller packs required by an active durable task in that list. A failed reload
retains the last valid registry. See the [ZIP format and limits](docs/EXTERNAL_BEHAVIOR_ZIPS.md).

## Registered catalog and item queries

The authoritative contract is bundled at
[`vendor/behavior-pack-registered.schema.json`](vendor/behavior-pack-registered.schema.json).
**File → Load registered catalog** accepts a compatible schema from the matching Behavior
repository's `contracts` directory. The candidate is validated before use; your graph stays
intact. This refresh applies to the current session. Revalidate before exporting.

For maintainers updating the bundled catalog:

```text
python make_catalog.py <path-to-behavior-repository-or-registered-schema>
python make_schema.py
```

Queries are explicit: `minecraft:coal` excludes charcoal, `@axe` uses Core's authoritative
item role, and `minecraft:coal|minecraft:charcoal` permits either. `ensure_equipment`
selects suitable carried equipment. Authorized chest acquisition and safe unloading
require durable task operations and explicit policy. Unknown container stock is not zero.
See [local preparation and recovery](docs/LOCAL_AUTONOMY.md) for the supported contracts.

## Validation

Run the complete suite from this repository's root:

```text
python -m unittest discover -s tests -v
```

GUI tests need a desktop display; on headless Linux use Xvfb to exercise them instead
of skipping them. Offline validation/export also works without importing Tkinter:

```text
python cli.py examples/custom/example_follow.samgraph --json-out follow.json --zip-out follow.zip
```

The dated [test report](docs/TEST_REPORT.md) distinguishes the current standalone checks
from earlier Forge/client validation. Studio's validator checks graph and export contracts;
actual gameplay still requires `/samcnpc behavior reload` and testing in Minecraft.
The included runtime fixture preserves the native-tested document without requiring
Behavior source code in a neighboring directory.

## License

[MIT](LICENSE).
