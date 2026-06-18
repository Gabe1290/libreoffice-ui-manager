# Architecture

## Overview

LOUIM consists of independent modules that communicate through a common internal model.

LibreOffice-specific code is isolated inside application providers.

The rest of the software remains application-independent.

---

# Main Components

## User Interface

Displays dialogs.

Allows users to:

- load templates
- save templates
- export templates
- export current interface
- restore defaults

---

## Core Engine

Coordinates every operation.

The Core Engine never communicates directly with LibreOffice.

---

## Discovery Engine

Discovers the current application interface.

Responsibilities:

- discover menus
- discover toolbars
- discover sidebar panels
- discover NotebookBar tabs
- discover commands

The Discovery Engine always identifies objects using UNO command IDs.

---

## Profile Manager

Maintains the current profile.

Responsible for validation, compatibility and serialization.

---

## Template Manager

Imports and exports `.louim` files.

---

## Apply Engine

Applies profiles to LibreOffice.

Shows or hides UI elements.

---

## Providers

Every LibreOffice application has its own provider.

Version 1:

- Writer Provider

Future:

- Calc Provider
- Impress Provider
- Draw Provider

---

# Internal Model

Every component works on a common internal representation.

Workspace

↓

Application

↓

UI Elements

↓

Profile

The user interface never manipulates LibreOffice directly.

Only the Discovery Engine and the Apply Engine communicate with LibreOffice.

