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
    ".uno:FileMenu": true,
    ".uno:EditMenu": true,
    ".uno:ViewMenu": false,
    ".uno:InsertMenu": false,
    ".uno:FormatMenu": true,
    ".uno:StylesMenu": false,
    ".uno:TableMenu": false,
    ".uno:FormMenu": false,
    ".uno:ToolsMenu": false,
    ".uno:WindowList": false,
    ".uno:HelpMenu": true
  },
  "toolbars": {}
}

## Canonical Identifiers

All templates must use LibreOffice UNO command IDs.

Localized names must never be stored.

The user interface will display localized names, but the template file always stores UNO IDs.