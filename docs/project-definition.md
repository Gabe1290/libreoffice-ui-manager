# LibreOffice UI Manager — Project Definition

## Purpose

LibreOffice UI Manager is an educational LibreOffice extension that allows teachers to progressively simplify the LibreOffice Writer interface for students and adult beginners.

The goal is not to lock users down, but to reduce cognitive overload while learners are introduced step by step to word processing.

## First target

The first working version focuses on LibreOffice Writer only.

Later versions may add Calc, Impress, and Draw.

## Educational goal

Teachers should be able to create, save, share, and import interface templates.

A template may show only the menus and tools needed for a specific lesson or learning stage.

Examples:

- Getting Started
- Basic Editing
- Document Layout
- Working with Images
- Tables
- Complete Writer

## Template files

Templates use the `.louim` extension.

A `.louim` file is a JSON file that describes which parts of the Writer interface should be visible or hidden.

Teachers can share these templates with students through Moodle, email, USB stick, or a shared school folder.

## Internationalization requirement

Templates must use LibreOffice UNO command IDs, not English menu names.

This is essential because Swiss schools may use LibreOffice in French, German, Italian, English, and other languages used by the international community.

For example, profiles should use identifiers such as:

- `.uno:FileMenu`
- `.uno:EditMenu`
- `.uno:ViewMenu`
- `.uno:InsertMenu`
- `.uno:FormatMenu`
- `.uno:StylesMenu`
- `.uno:TableMenu`
- `.uno:FormMenu`
- `.uno:ToolsMenu`
- `.uno:HelpMenu`

The visible labels shown to users can be localized, but the stored configuration must remain language-independent.

## Future enhancement

Later, LibreOffice UI Manager may become more than an interface manager.

A future `.louim` template could also include:

- a welcome message for learners,
- lesson objectives,
- teacher notes,
- links to exercises,
- hints for students.

This enhancement should be kept in mind during development, but it is not part of the first working version.

## Version 1 goal

Version 1 should provide:

- Writer support only
- import `.louim` template
- export `.louim` template
- hide/show top-level Writer menus
- restore full Writer interface
- use UNO command IDs internally
- work on Windows, Linux, and macOS

## Important planned feature: Export current interface

LibreOffice UI Manager should include an option:

**Export current Writer interface as template**

This allows a teacher to manually customize LibreOffice Writer first, then export the visible/hidden interface state as a reusable `.louim` template.

This is important because teachers may prefer to prepare the interface visually instead of writing JSON by hand.

The exported template must still store menu and command information using LibreOffice UNO command IDs, not localized menu names.