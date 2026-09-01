# Project Definition

# LibreOffice UI Manager (LOUIM)

## Mission

LibreOffice UI Manager (LOUIM) is an educational LibreOffice extension designed to progressively simplify the LibreOffice user interface.

Its objective is to allow teachers to reveal only the functionality required for the current lesson, reducing cognitive overload while students learn.

LOUIM is intended for:

- Schools
- Adult education
- Digital literacy programmes
- Public libraries
- Self-learning

---

# Objectives

LOUIM allows users to:

- discover the current LibreOffice interface
- create interface profiles
- import profiles
- export profiles
- export the current interface as a template
- progressively reveal new functionality

---

# Supported Applications

Version 1 supported only LibreOffice Writer. As of version 4.0.0, LOUIM
supports all four core LibreOffice applications:

- Writer
- Calc
- Impress
- Draw

Support for Calc, Impress, and Draw was added without changing the
architecture, as planned: each is a `Module` descriptor plus starter
templates, not a redesign. See [architecture.md](architecture.md).

---

# Templates

Templates use the `.louim` extension.

Templates are JSON documents.

Templates are language-independent.

Templates store UNO command identifiers.

---

# Educational Philosophy

LOUIM's purpose is to simplify learning, not to hide functionality permanently.

Teachers remain in complete control of the learning progression.

---

# Long-Term Vision

Eventually LOUIM should become the reference educational interface manager for LibreOffice.

