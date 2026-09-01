# Teacher Guide

Everything a teacher needs to run LOUIM in a classroom, without touching
code. For installation, see the [README](../README.md#install). This guide
covers what to do once it's installed.

## The menu

After installing, every supported app (Writer, Calc, Impress, Draw) gets a
LibreOffice UI Manager menu with four commands. Configure Menus lets you
tick or untick whole top-level menus. Choose Template applies a `.louim`
file, bundled or your own. Save Current Layout as Template snapshots
whatever the interface looks like right now into a `.louim` file you can
reuse or share. Restore Full Menus undoes everything LOUIM has changed, back
to LibreOffice's own defaults.

## The fastest way to simplify an interface

For most classroom needs you never need to touch a `.louim` file at all.
Configure Menus opens a dialog listing the app's top-level menus, File,
Edit, View, Insert, Format, Table, Tools, and so on, with a tickbox each.
Untick a menu and it disappears from the menu bar entirely. This is stronger
than LibreOffice's own Tools ▸ Customize, which can empty a built-in menu of
its items but always leaves the now-empty menu sitting on the bar.

File, Edit, and Help stay ticked no matter what and can't be unticked.
They're a universal convention across every desktop application, and Help is
also where LOUIM's own menu lives, so keeping it means there's always a way
back to Restore Full Menus.

The dialog can save its result as a template in the same step. A five-second
tidy-up becomes a reusable profile for next time.

## Using the bundled templates

Each app ships three starter templates in `templates/<app>/`.
`<app>-level-1.louim`, called "Getting Started," is the smallest interface.
It hides View, Insert, Table, and Tools, keeps File, Edit, Format, and Help,
and trims the toolbars to match. `<app>-level-2.louim`, "Basic Editing,"
re-adds Insert, View, and Table for learners who are ready to use them,
while still hiding Styles and Tools. `<app>-full.louim`, "Complete," shows
every menu. It's equivalent to Restore Full Menus, but available as a
template from the picker.

Choose Template opens a file picker already pointed at the active app's own
template folder, so Writer only shows Writer templates and Calc only shows
Calc's. You can't accidentally apply a Calc profile to Writer.

A typical progression through a course starts the whole class on
`writer-level-1`, moves individuals or the whole group to `writer-level-2`
once they're comfortable with paragraphs and basic formatting, then applies
`writer-full`, or clicks Restore Full Menus, once the training-wheels phase
is over.

## Making your own template

There are two ways to do this, from easiest to most control. The first is
Configure Menus, then Save: untick the menus you want gone and save as a
template. This works well for "remove a few whole menus" profiles. The
second is to set up the interface by hand and then use Save Current Layout
as Template. Use Tools ▸ Customize to hide individual toolbar buttons or
menu items rather than whole menus, arrange toolbars, hide sidebar panels
through the sidebar's own menu, then export. LOUIM's export captures all of
it: which menus and individual menu items are visible, which toolbars and
toolbar buttons are showing, and which sidebar decks (Properties, Styles,
Gallery, and so on) are present, item by item rather than just whole
surfaces.

Templates save to `Documents/LOUIM templates` by default, so they survive a
LibreOffice reinstall or extension update. The extension's own storage does
not.

## Hand-editing a `.louim` file

A saved template is plain, readable JSON, and you can open it in any text
editor. See [template-format.md](template-format.md) for the full field
reference. The short version: every section maps an identifier to `true` to
show it or `false` to hide it, and anything not mentioned defaults to shown.
Two things are worth knowing before editing by hand. Identifiers are
LibreOffice's own internal command names, like `.uno:InsertMenu`, not the
menu labels you see on screen. That's what makes a template work in any
LibreOffice language. Use Choose Template after any edit to check it still
loads; a typo in an identifier is silently ignored rather than raised as an
error, so the item just stays at its default. Setting
`"hide_toolbar_buttons_with_menus": true` automatically drops the toolbar
icon for anything hidden in `"menus"`, so you don't have to hide the same
feature twice.

## Restoring

Restore Full Menus reverts every surface LOUIM has changed, menus,
toolbars, toolbar buttons, sidebar decks, and extension menus, back to
exactly what they were before LOUIM touched them, independent of which
template, if any, was last applied. It's always safe to click if something
looks wrong.

## Common questions

Will a template break if a student's LibreOffice is in a different language?
No. Templates never store menu labels, only LibreOffice's internal
identifiers, so the same `.louim` file works in English, French, German, or
Italian LibreOffice without changes.

I applied a template, then applied another. Did they combine? No. Applying
is never cumulative. The second template's menus, toolbars, and toolbar
items get computed fresh from LibreOffice's own factory defaults, so
applying template B after template A gives you exactly B.

Does this work the same in Calc, Impress, and Draw? Yes, the same four menu
commands, the same template format, the same behavior. Only the menu names
and toolbar contents differ per app, and each has its own starter templates
under `templates/<app>/`.

Is this a lockdown tool? No, and [VISION.md](../VISION.md) says as much.
Nothing LOUIM hides is deleted. Every hidden feature is one Restore Full
Menus away, and a template is meant to change as a learner's skills grow,
not to permanently restrict what they can do.
