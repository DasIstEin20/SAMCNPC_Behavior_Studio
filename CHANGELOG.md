# 1.2.0 distribution update — 2026-09-28

- Publish a self-contained Git repository with the existing logo and English-first
  README, plus Polish and German pages linked through a language menu.
- Adapt the six themed PDF manuals into three illustrated GitHub Markdown guides:
  retain all 20 chapters and command examples, with a new Guardian/Forester chapter.
- Bundle the tutorial projects and native-tested fixture; preserve both regression
  assertions while removing dependencies on neighboring source checkouts.
- Include the 33-rule / 506-node Guardian/Forester graph, JSON, ZIP, screenshots and
  dated validation. The editor/runtime formats and application version remain 1.2.0.

# 1.2.0 — 2026-09-27

Registered-schema-driven nodes, validated item queries, local preparation example, direct external ZIP export/install, transactional catalog refresh and safe install backups. English remains the default; project format 1 and live EN/PL/DE switching are retained.

# 1.1.1 — 2026-09-26

- Start in English; retain live PL/EN/DE switching.
- Translate the existing UI without destroying menus, selectors or the editor.
- Preserve user drafts, selection, undo, tab and viewport across language changes.
- Keep scheduled Tk callbacks intact.
- Reuse native fonts and bound text-fitting work on large graphs.
- Log unexpected Python callback errors and preserve launcher failure output.
- Add regression tests for actual dropdown/menu interactions and editor state.

Existing projects and runtime JSON remain compatible. No change to Minecraft
mods, the local pack validator, the component catalog or bundled logo.

Windows-specific crash reproduction remains unverified; Linux/Xvfb tests passed.
