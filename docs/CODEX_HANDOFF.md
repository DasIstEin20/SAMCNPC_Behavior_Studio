> Historical 1.1.1 reference. Current 1.2.0 uses the bundled registered catalog (25 conditions / 25 actions). See README and TEST_REPORT for current behavior and validation.

# Behavior Studio 1.1.1 — language-switch hotfix

User reported the Python editor exits when changing the UI to English or German.
They requested English as the default. Scope is the editor only; no Minecraft mod
or behavior-pack runtime semantics were changed.

## Findings and fix

The supplied 1.1 ZIP's `set_language` destroyed every root child (including the
menu and initiating language combobox), cancelled ALL Tcl `after` entries, then
rebuilt the entire UI synchronously inside the selection callback. This is a
risky native-widget lifetime pattern, and also lost selection, tab and viewport.
The original 71 tests pass on Linux: they did not reproduce the reported Windows
process crash. Do not claim Windows reproduction or a universal platform fix.

1.1.1 constructs the UI once. Weak widget registrations hold translation
resolvers; menu labels, tab captions, canvas captions, inspector labels, palette,
help, installation text and validation report update in place. The callback does
not call `_build`, `destroy`, `update`, `update_idletasks` or `after_cancel`.
Unapplied data and field widgets stay intact. Language is presentation state:
never change pack IDs, rule IDs, arguments or descriptions authored by the user.

`DEFAULT_LANGUAGE = "en"`; English at each launch, PL and DE selectable.
No persistent preference/config format was introduced.

Added Python callback/startup diagnostics. The Windows launcher retains a nonzero
exit code and terminal output; `-X faulthandler` also prints native fatal faults.
A native fatal Tcl/Windows failure is NOT catchable by the Python callback hook.

## Validation

95 tests PASS on Python 3.13.5 / Tk 8.6.16 / Linux + Xvfb. GUI tests now fail on
uncaught Python callbacks and Tcl `bgerror`, instead of treating unexpected Tcl
construction errors as a skipped test. Tests include real popup mouse selection,
menu invocation, persistent widget identity, timers, all 38 registered components,
unapplied drafts, undo/cursor, tabs, zoom, palette selection and unchanged export.
See TEST_REPORT.md and python-test-results.txt. Validate native Windows next.

## Files left unchanged by this hotfix

engine.py, catalog/schema, Behavior JSON and samgraph examples, logo. Legacy
`.samgraph` has the same data format. No GitHub access is needed at runtime.

## Remaining scope

This is still a source-derived local validator, not the Forge compiler. This
change does not add datapacks, language translations for all engine diagnostics,
new Behavior operations, or a Windows executable. Preserve the original editor
architecture and avoid whole-widget reconstruction for localization.
