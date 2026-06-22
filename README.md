# LibreOffice UI Manager

LibreOffice UI Manager (LOUIM) is an educational tool for simplifying the
LibreOffice interface.

Its goal is to help students and adult beginners learn word processing progressively, without being overwhelmed by too many menus and options.

**Version 2.0.0** — stable release for LibreOffice **Writer** and **Calc**.
Available in English, French, German, and Italian.

## Install

1. Download `louim.oxt` from the
   [latest release](https://github.com/Gabe1290/libreoffice-ui-manager/releases).
2. In LibreOffice: **Tools ▸ Extension Manager… ▸ Add…**, pick `louim.oxt`, and
   restart LibreOffice.
3. A **LibreOffice UI Manager** menu appears in Writer: *Apply Template…*,
   *Save Current Layout as Template…*, *Restore Full Menus*.

Or build it yourself with `python tools/build.py` (output in `dist/louim.oxt`).

## Supported applications

Writer and Calc. (Impress and Draw are on the roadmap and follow the same
module pattern.)

## Main idea

Teachers can create and share interface templates such as:

- Writer / Calc — Level 1
- Writer / Calc — Level 2
- Full Writer / Full Calc

Students can import a template and work with a simplified LibreOffice Writer or Calc interface.

## Template format

Templates use the `.louim` extension and are written in JSON.