# Glossary

Terms used across LOUIM's docs, code, and `.louim` files.

**`.louim` file / template.** A JSON file describing which parts of a
LibreOffice application's interface are shown or hidden. The full schema is
in [template-format.md](template-format.md). You apply one with Choose
Template, produce one with Save Current Layout as Template, or just hand-edit
it in any text editor.

**Application / module.** Which LibreOffice app a template targets, `writer`,
`calc`, `impress`, or `draw`, stored in a template's `"application"` field.
Internally each app is represented by a `Module` descriptor
(`src/louim/adapters/modules.py`) bundling the identifiers LOUIM needs to act
on it. See [architecture.md](architecture.md).

**UNO command ID.** LibreOffice's internal, language-independent name for a
menu command, such as `.uno:InsertMenu` or `.uno:InsertPagebreak`. This is
what `.louim` files store instead of a menu's visible label, so a template
works in any LibreOffice language. See
[ADR 0001](adr/0001-use-uno-command-ids.md). You can find one for a command
with `tools/discover-menus.py --tree`, a developer tool; see
[developer-guide.md](developer-guide.md).

**Toolbar resource URL.** The identifier for a whole toolbar, like
`private:resource/toolbar/standardbar`, used as the `toolbars` section's key.
This is a different namespace from a UNO command ID: a toolbar as a whole has
a resource URL, while the buttons inside it have command IDs, used in
`toolbaritems`.

**Deck (sidebar deck).** One panel of the sidebar, such as Properties,
Styles, Gallery, or Navigator. Identified by a deck Id, like `GalleryDeck`,
in a template's `sidebar` section.

**Addon menu.** A top-level menu contributed by an extension other than
LOUIM, for example Dmaths, not part of LibreOffice's own built-in menu bar.
Identified by its configuration node name in a template's `addons` section.
LOUIM's own menu can never be hidden this way.

**Profile.** An informal term for the settings inside a `.louim` template.
It isn't a class or object in the code; see
[ADR 0004](adr/0004-workspace-concept.md). The template dict is the profile.

**Apply / Restore.** Apply sets the interface to match a template, and it's
always non-cumulative: it starts from LibreOffice's own defaults, or for
sidebar and addons, from whatever the interface looked like before LOUIM
touched it, and it never stacks on top of the previous template. Restore
reverts everything LOUIM has changed back to exactly what it was before,
independent of which template, if any, was last applied.

**Discovery.** Reading the live LibreOffice interface, what
menus, toolbars, decks, and addons currently exist, rather than working from
a hardcoded list. See [discovery-engine.md](discovery-engine.md) and
[ADR 0002](adr/0002-discovery-engine.md).

**Level (level-1 / level-2 / full).** Not a LOUIM concept in the code, just
the naming convention the bundled starter templates use for a progression
from a minimal interface (level-1) through an intermediate one (level-2) to
everything (full). See the [teacher guide](teacher-guide.md).

**Configure Menus.** The in-app dialog for removing whole top-level menus
without hand-editing a `.louim` file. See the teacher guide.

**Protected menus.** File, Edit, and Help, the three top-level menus LOUIM
will never hide, whether from a template or from Configure Menus.
[PROJECT.md](../PROJECT.md) explains why this rule exists.

**LOUIM.** LibreOffice UI Manager, this project. Not to be confused with
LONBM (LibreOffice Notebookbar Manager), a separate companion project that
manages the tabbed "Notebookbar" UI mode. LOUIM deliberately stays out of
that. See [HANDOFF.md](../HANDOFF.md).
