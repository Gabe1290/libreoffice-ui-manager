# LibreOffice UI Manager

> **📢 This project has moved to GitLab — [gitlab.com/gthullen-group/libreoffice-ui-manager](https://gitlab.com/gthullen-group/libreoffice-ui-manager).**
> Development, issues, and releases now happen there. This GitHub repository is a read-only mirror.

LibreOffice UI Manager (LOUIM) is an educational tool for simplifying the
LibreOffice interface.

Its goal is to help students and adult beginners learn word processing progressively, without being overwhelmed by too many menus and options.

**Version 4.2.1** — stable release for LibreOffice **Writer**, **Calc**,
**Impress**, and **Draw**. Available in English, French, German, and Italian.

## Install

1. Download `louim.oxt` from the
   [latest release](https://gitlab.com/gthullen-group/libreoffice-ui-manager/-/releases)
   (attached as a release asset). **Keep the filename `louim.oxt` — do not
   rename it.** LibreOffice uses the `.oxt` filename as the extension's package
   name, and the menu commands reference `louim.oxt`; a renamed file makes
   *Apply Template* fail with `KeyError: 'louim.oxt'`.
2. In LibreOffice: **Tools ▸ Extension Manager… ▸ Add…**, pick `louim.oxt`, and
   restart LibreOffice.
3. A **LibreOffice UI Manager** menu appears in each supported app (Writer,
   Calc, Impress, Draw): *Apply Template…*, *Save Current Layout as Template…*,
   *Restore Full Menus*.

> **Stuck on a repeating "…already installed. Replace?" prompt at startup?**
> Just click **Cancel** — the extension is already installed and works fine;
> Cancel simply dismisses the repeat attempt. This can happen if you install by
> **double-clicking** the `.oxt` (a second LibreOffice tries to register it while
> the Quickstarter still holds the extension database, so the install keeps
> retrying). Installing via **Extension Manager ▸ Add** avoids it entirely.

Or build it yourself with `python tools/build.py` (output in `dist/louim.oxt`).

## Supported applications

Writer, Calc, Impress, and Draw — every core LibreOffice application.

## Main idea

Teachers can create and share interface templates such as:

- Writer / Calc — Level 1
- Writer / Calc — Level 2
- Full Writer / Full Calc

Students can import a template and work with a simplified LibreOffice Writer or Calc interface.

## Template format

Templates use the `.louim` extension and are written in JSON.

## License

LOUIM is free software, released under the
[Mozilla Public License 2.0](LICENSE).