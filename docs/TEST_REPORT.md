# 2026-09-28 — standalone Git publication

From the standalone Studio repository, on Windows / Python 3.10 / real Tk:
`python -m unittest discover -s tests -v` — **105 passed, 0 failed, 0 skipped**
in **19.379 s**. The full suite exercises real GUI controls, catalog-generated fields,
EN/PL/DE switching, the old Guardian project, the 506-node Guardian/Forester project,
JSON roundtrip, ZIP export, fake-instance installation, backup and rejection paths.

Two tests previously read files from sibling Behavior/guide directories. Their inputs
are now included at `tests/fixtures/guardian_forester_forge.zip` and
`tutorials/examples/complex_guardian_escort.samgraph`; the assertions are preserved.
The first standalone packaging run caught an omitted fixture caused by the workspace's
local `*.zip` exclusion. Both required ZIP inputs were explicitly included before the
passing full rerun. No test was removed, disabled or changed to skip the missing file.

Publication checks: 281 local links/anchors across the four README entry points and
three tutorial pages; case-sensitive path checks; 23 image references; unchanged native
fixture bytes; actual CLI JSON/ZIP export parity. The three Markdown guides preserve all
20 original chapters and all 14 command/path example lines per language, with one added
advanced-example chapter each. HTML rendering preserved the 21 chapter targets and five
image references per guide. These are repository Markdown pages, not a separate website.
The original six themed PDFs remain in the local guide distribution and are not published
in this repository. Screenshots are shared with the original guide source, not recreated.

This publication changes documentation and test packaging only. Studio behavior,
Core/Behavior/LLM source and runtime contracts are unchanged by this publication step.
Existing trailing whitespace was removed from three files; Python AST parity was verified.
The native Forge/client evidence below and in the example's validation report belongs to
the earlier dated workspace campaign; those Minecraft suites were not rerun for this step.
Raw publication logs and HTML checks are retained in the canonical workspace's local
`autonomy/` directory; they are not needed to run this standalone repository.

# 2026-09-28 — advanced Guardian/Forester user workflow

Windows / Python 3.10 / real Tk: **105 tests PASS** (18.952 s).
Two new user scenarios exercise the actual 506-node project through Open, Validate,
EN/PL/DE switching, JSON/ZIP export, JSON reimport, instance selection, ZIP install,
overwrite backup, duplicate-ID rejection and invalid-query export blocking.
After adding artifact parity assertions, both new scenarios passed again (3.399 s).
The bundled samgraph/JSON/ZIP and real Forge ZIP fixture contain the same document.
Actual Studio window captures are alongside the project in
`examples/advanced/guardian_forester/`. No Studio production-code changes were needed.

The real Forge combined full-inventory / missing-axe scenario found a Behavior
preparation-cooldown bug, fixed generically in Behavior and retained as a regression.
See the example's `VALIDATION.md` and the root `PROJECT_STATE.md` for native evidence.
Earlier reports below retain their original date and scope.

# Studio 1.2.0 — current Windows evidence, 2026-09-27

103/103 tests PASS using `python -m unittest discover -s tests -v`; log in workspace `autonomy/run-20260927-local-autonomy/studio-final-06.log`. All 50 registered components inspected in EN/PL/DE; native combobox/menu switching, drafts/history preserved; old Guardian project imports; JSON/ZIP validation, export, install paths, duplicate and backup checks pass. Actual GUI launched and screenshots visually inspected. Forge scenario `actualStudioExportLoadsAsExternalZipAndEquipsThroughRegisteredRules` loads the real exported archive and verifies physical equipment.

The evidence below is historical and has not been relabeled as this build.

# SAMCNPC Behavior Studio 1.1.1 — verification

Date: 2026-09-26
Environment: Linux/Xvfb, Python 3.13.5, Tk 8.6.16.
Behavior target: b92ec0e23164f822f450fc65a006ce9039cec37a (unchanged).

## Final automated suite

Command: `xvfb-run -a python -m unittest discover -s tests -v`

**95 passed; 0 failed; 0 skipped.**
The final run is in `python-test-results.txt`.

Coverage added to the inherited suite:
- English startup default and English localization fallback;
- real combobox dropdown mouse-selection/release bindings;
- language menu invocation, repeated PL/EN/DE switches;
- stable identity of the canvas, notebook, menu, combobox, About image and text fields;
- preservation of application/Tk scheduled callbacks;
- JSON, metadata and inspector drafts; JSON cursor and native text undo;
- project state, undo history, selection, active tab, pan/zoom and install fields;
- every registered condition/action inspected in all UI languages;
- unchanged runtime JSON after language changes;
- localization key and placeholder parity, complete EN/DE component catalog;
- bounded native-font/text-fitting caches and pixel-width checks;
- callback/startup diagnostic log writing and rotation.

GUI tests collect Python callback exceptions and Tcl `bgerror` explicitly.
Supplying DISPLAY then encountering an unexpected construction TclError fails a
test instead of turning it into a misleading skip.

## Additional real-project smoke

Imported the supplied `complex_guardian_escort.samgraph` (80 nodes, 71 edges).
Twelve consecutive language switches alternated between the combobox virtual
selection event and the actual menu command. No Python/Tcl errors occurred;
project state and exported runtime JSON stayed unchanged. The actual default-EN,
German and About interfaces were captured and visually inspected.

A preliminary 60-switch test and a 12-switch test exceeded the tool's 45-second
wall budget. Stack sampling localized the work to repeated Tk font construction
and character-by-character width measurement on the 80-node graph (not a proven
native crash). After adding reused fonts, bounded fit results and binary-search
text fitting, the 12-switch smoke completed. The 60-switch run was not repeated
and is NOT claimed as passing.

## Baseline and limitations

The original 1.1 ZIP's 71 tests passed on this Linux environment. The reported
Windows process exit was NOT reproduced here. Source inspection did confirm the
old handler destroyed its initiating menu/combobox, the entire widget tree and all
scheduled interpreter callbacks. The hotfix removes that lifetime pattern instead
of rebuilding the UI from a selection callback.

Native Windows execution, Windows batch-launcher behavior and Windows/Tk-version
specific crashes still require a check on the user's machine. No EXE was built.
No Forge/Minecraft runtime was started. No behavior pack semantics, engine,
vendored catalog/schema or logo changed.
