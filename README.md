# LibreOffice UI Manager

LibreOffice UI Manager (LOUIM) is an educational tool for simplifying the
LibreOffice interface.

Its goal is to help students and adult beginners learn word processing progressively, without being overwhelmed by too many menus and options.

**Version 1.0.0** — stable release for LibreOffice **Writer**. Available in
English, French, German, and Italian.

## Install

1. Download `louim.oxt` from the
   [latest release](https://github.com/Gabe1290/libreoffice-ui-manager/releases).
2. In LibreOffice: **Tools ▸ Extension Manager… ▸ Add…**, pick `louim.oxt`, and
   restart LibreOffice.
3. A **LibreOffice UI Manager** menu appears in Writer: *Apply Template…*,
   *Save Current Layout as Template…*, *Restore Full Menus*.

Or build it yourself with `python tools/build.py` (output in `dist/louim.oxt`).

## First target

Writer only.

## Main idea

Teachers can create and share interface templates such as:

- Writer Level 1
- Writer Level 2
- Full Writer

Students can import a template and work with a simplified LibreOffice Writer interface.

## Template format

Templates use the `.louim` extension and are written in JSON.