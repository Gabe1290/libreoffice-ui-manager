# LOUIM Template Format

LOUIM templates use the `.louim` file extension.

A `.louim` file is a JSON file that describes a simplified LibreOffice interface profile.

## Design rule

Templates must use LibreOffice UNO command IDs, not visible menu labels.

This makes templates independent of the LibreOffice language.

## Minimal example

```json
{
  "version": 1,
  "application": "writer",
  "profile": {
    "name": "Getting Started",
    "description": "Very simple Writer interface for beginners."
  },
  "menus": {
    ".uno:PickList": true,
    ".uno:EditMenu": true,
    ".uno:ViewMenu": false,
    ".uno:InsertMenu": false,
    ".uno:FormatMenu": true,
    ".uno:FormatStylesMenu": false,
    ".uno:TableMenu": false,
    ".uno:FormatFormMenu": false,
    ".uno:ToolsMenu": false,
    ".uno:WindowList": false,
    ".uno:HelpMenu": true
  },
  "addons": {},
  "toolbars": {}
}
```

Note: `.uno:PickList` is the File menu, `.uno:FormatStylesMenu` is Styles, and
`.uno:FormatFormMenu` is Form. Use `tools/discover-menus.py` against a running
LibreOffice to list the exact IDs for your version.

## Canonical Identifiers

All templates must use LibreOffice UNO command IDs.

Localized names must never be stored.

The user interface will display localized names, but the template file always stores UNO IDs.

## Built-in menus

The `menus` object maps a top-level menu's UNO command ID to a boolean
(`true` = visible, `false` = hidden). Hidden menus are removed from Writer's
menu bar; everything else stays. Commands not listed default to visible.

## Extension menus

The optional `addons` object hides or shows menus contributed by **other
LibreOffice extensions** (for example, a maths add-on). These are not part of
the built-in menu bar, so they are keyed by the extension's stable
configuration node name rather than a `.uno:` command:

```json
"addons": {
  "org.openoffice.Office.addon.aide": false
}
```

Run `tools/discover-menus.py` to list the extension menus available in Writer
and their node names. LOUIM never hides its own menu.