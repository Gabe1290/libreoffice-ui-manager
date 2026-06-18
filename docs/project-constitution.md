# LibreOffice UI Manager (LOUIM)

# Project Constitution

Version 1.0

---

## Purpose

This document defines the architectural principles of LibreOffice UI Manager.

These principles guide every design decision.

They should only be changed after careful consideration because they define the identity of the project.

---

# Principle 1 — Educational First

LOUIM exists to improve the teaching and learning of LibreOffice.

Every feature should make LibreOffice easier to learn.

LOUIM is not primarily a security or lockdown tool.

---

# Principle 2 — Progressive Disclosure

Learners should only see the tools they need today.

Teachers decide when additional functionality is introduced.

---

# Principle 3 — Language Independence

All internal identifiers must use LibreOffice UNO command IDs.

Localized menu names must never be stored inside templates.

This guarantees compatibility across all LibreOffice languages.

---

# Principle 4 — Dynamic Discovery

LOUIM should discover the current LibreOffice interface whenever possible.

Hardcoded interface definitions should only be used as compatibility fallbacks.

---

# Principle 5 — Separation of Responsibilities

The project follows three architectural layers.

## Model

Represents data.

Examples:

* Workspace
* Profile
* UIElement

## Engine

Processes data.

Examples:

* Discovery Engine
* Template Manager
* Apply Engine

## User Interface

Allows users to interact with LOUIM.

---

# Principle 6 — LibreOffice Isolation

The Core Engine must never communicate directly with LibreOffice.

Communication with LibreOffice occurs only through application adapters.

Example:

* Writer Adapter
* Calc Adapter
* Impress Adapter
* Draw Adapter

---

# Principle 7 — Application Independence

The Core Engine should not contain application-specific code.

Adding support for a new LibreOffice application should require only a new adapter.

---

# Principle 8 — Templates are Data

`.louim` files are data only.

Reading and writing templates is the sole responsibility of the Template Manager.

No other component should manipulate JSON directly.

---

# Principle 9 — Cross-platform

LOUIM must work on:

* Linux
* Windows
* macOS

using a single code base.

---

# Principle 10 — Extensibility

Future features should be added without redesigning the architecture.

Examples include:

* lesson objectives
* teacher notes
* student hints
* educational resources
* additional LibreOffice applications

---

# Principle 11 — Simplicity

When multiple technical solutions exist, prefer the simplest solution that satisfies the educational goals.

---

# Principle 12 — Documentation First

Architecture and documentation are considered part of the source code.

Major architectural decisions should be documented before implementation.

---

## Motto

> **The interface adapts to the learner — not the learner to the interface.**
