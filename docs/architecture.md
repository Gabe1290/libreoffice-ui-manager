# LibreOffice UI Manager (LOUIM)

# Architecture

Version 1.0 (Draft)

---

# 1. Purpose

LibreOffice UI Manager (LOUIM) is an educational LibreOffice extension whose purpose is to progressively simplify the LibreOffice user interface for teaching and learning.

LOUIM is **not** intended to lock down LibreOffice. Instead, it allows teachers to reveal functionality gradually as learners become more comfortable with the application.

The first supported application is **LibreOffice Writer**.

Support for Calc, Impress and Draw will be added later without changing the overall architecture.

---

# 2. Design Principles

## Educational First

Every design decision should support teaching and learning.

The objective is to reduce cognitive load while allowing teachers complete flexibility.

---

## Language Independence

LOUIM must never rely on localized menu names.

All internal data must use LibreOffice UNO command identifiers.

Example:

```
.uno:FileMenu
```

instead of

```
File
Fichier
Datei
File
```

This guarantees that templates work on every LibreOffice language.

---

## Dynamic Discovery

LOUIM should discover the current LibreOffice interface whenever possible.

The extension should not rely on hardcoded menu definitions except as a compatibility fallback.

---

## Cross Platform

LOUIM must work on

* Linux
* Windows
* macOS

using the same source code.

---

## Modular Design

Each LibreOffice application is implemented as an independent provider.

The core of LOUIM should not contain application-specific code.

---

# 3. High-Level Architecture

```
+---------------------------+
|      LibreOffice UI       |
+-------------+-------------+
              |
              |
+-------------v-------------+
|     LOUIM User Interface  |
+-------------+-------------+
              |
              |
+-------------v-------------+
|        Core Engine        |
+-------------+-------------+
              |
    +---------+---------+
    |                   |
+---v---+           +---v---+
|Import |           |Export |
+-------+           +-------+
    |                   |
+---v-------------------v---+
|      Profile Manager      |
+-------------+-------------+
              |
+-------------v-------------+
|    Discovery Engine      |
+-------------+-------------+
              |
      Writer Provider
```

---

# 4. Main Components

## User Interface

Responsible for:

* loading templates
* saving templates
* importing templates
* exporting templates
* applying templates
* restoring defaults

---

## Discovery Engine

Discovers the current Writer interface.

Responsible for identifying:

* menus
* toolbars
* sidebar decks
* notebook bar tabs
* commands

All discovered items are identified using UNO command IDs.

---

## Profile Manager

Maintains the internal representation of a Writer profile.

Responsible for:

* loading
* saving
* validation
* compatibility checking

---

## Import / Export

Imports and exports `.louim` template files.

The export module should also support:

**Export Current Writer Interface**

This allows a teacher to visually configure Writer and immediately create a reusable template.

---

## Providers

Every LibreOffice application has its own provider.

Version 1 contains only:

```
Writer Provider
```

Future versions will add:

```
Calc Provider

Impress Provider

Draw Provider
```

without requiring changes to the core engine.

---

# 5. Internal Data Model

The core engine works with an internal interface model.

```
Application

Menus

Toolbars

Sidebar

NotebookBar

Commands
```

Every operation works on this model.

Templates are only a serialized representation of this structure.

---

# 6. Template Philosophy

Templates represent an educational state of the user interface.

Examples include:

* Getting Started
* Basic Editing
* Document Layout
* Working with Images
* Complete Writer

Templates should never depend on the language of LibreOffice.

---

# 7. Future Expansion

Possible future features include:

* lesson objectives
* welcome messages
* teacher notes
* student hints
* links to learning material

These features are intentionally outside Version 1.

The architecture should allow them to be added without redesigning the core.

---

# 8. Version 1 Scope

Version 1 should implement only:

* Writer support
* dynamic interface discovery
* profile manager
* template import
* template export
* export current interface
* apply profile
* restore default interface

Everything else belongs to future milestones.

---

# 9. Development Workflow

For every new feature:

1. Update the documentation.
2. Implement the feature.
3. Test on Linux.
4. Test on Windows.
5. Test on macOS.
6. Commit to Git.
7. Create a tagged milestone when appropriate.

Documentation is considered part of the source code and should remain synchronized with the implementation.

## Workspace

A Workspace represents the currently active LibreOffice application together with its interface and active profile.

A Workspace contains:

- Application
- UI Elements
- Active Profile