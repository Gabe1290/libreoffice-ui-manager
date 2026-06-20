# LibreOffice UI Manager — extension entry points.
#
# These functions are the bridge between the LibreOffice menu (Addons.xcu) and
# the LOUIM engine. Each is exported through ``g_exportedScripts`` so the bundled
# Python script provider can invoke it from a ``vnd.sun.star.script:`` menu URL.
#
# The engine itself (discovery, template loading, apply/restore) lives in the
# ``louim`` package and is unit/headlessly tested separately. This module only
# handles the LibreOffice-facing glue: file picking and message boxes.

import os
import sys

import uno

# Extension identifier from description.xml — used to locate the deployed
# package on disk so the bundled ``louim`` Python package becomes importable.
_EXTENSION_ID = "org.louim.libreoffice-ui-manager"


def _package_url(ctx):
    """Return the deployed extension's location as a file URL, or None.

    The deployment ``PackageInformationProvider`` is the reliable way to find
    where this .oxt was installed (the script provider gives this module no
    usable filesystem ``__file__``). Both the bundled Python package and the
    starter ``templates/`` folder live under this location, mirroring the .oxt
    layout.
    """
    try:
        pip = ctx.getValueByName(
            "/singletons/com.sun.star.deployment.PackageInformationProvider"
        )
        return pip.getPackageLocation(_EXTENSION_ID) or None
    except Exception:  # noqa: BLE001
        return None


def _ensure_package_path(ctx):
    """Make the bundled ``louim`` package importable from inside the extension.

    The script provider does not put the package root on ``sys.path``. The
    bundled Python lives in the deployed package's ``python/`` subfolder
    (mirroring the .oxt layout), so adding that makes ``import louim.*`` resolve
    exactly as it does for the dev tools and tests.
    """
    url = _package_url(ctx)
    if not url:
        return
    try:
        python_dir = os.path.join(uno.fileUrlToSystemPath(url), "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)
    except Exception:  # noqa: BLE001 — fall back to whatever path is already set
        pass


def _message_box(ctx, title, message):
    """Show a simple OK info box parented to the current document window."""
    from com.sun.star.awt.MessageBoxType import INFOBOX
    from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK

    smgr = ctx.getServiceManager()
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    frame = XSCRIPTCONTEXT.getDesktop().getCurrentFrame()
    window = frame.getContainerWindow() if frame else None

    box = toolkit.createMessageBox(window, INFOBOX, BUTTONS_OK, title, message)
    box.execute()


def _pick_template(ctx):
    """Open a file picker for a .louim template; return a system path or None."""
    from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

    smgr = ctx.getServiceManager()
    picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker", ctx
    )
    picker.setTitle("Choose a LOUIM template")
    picker.appendFilter("LOUIM templates (*.louim)", "*.louim")
    picker.appendFilter("All files (*.*)", "*.*")

    # Default to the starter templates bundled inside the deployed extension so
    # teachers land on writer-level-1/2 without hunting for a file. Best-effort:
    # if the folder can't be located the picker just opens at its last location.
    url = _package_url(ctx)
    if url:
        templates_url = url.rstrip("/") + "/templates"
        try:
            if os.path.isdir(uno.fileUrlToSystemPath(templates_url)):
                picker.setDisplayDirectory(templates_url)
        except Exception:  # noqa: BLE001
            pass

    if picker.execute() != OK:
        return None
    files = picker.getSelectedFiles()
    return uno.fileUrlToSystemPath(files[0]) if files else None


def hello(*args):
    """Temporary smoke-test entry point for the first LOUIM extension."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _message_box(ctx, "LibreOffice UI Manager", "Hello from LOUIM")
    except Exception as exc:  # noqa: BLE001 — surface any glue failure to the log
        print("LOUIM error:", exc)


def apply_template(*args):
    """Pick a .louim template and apply its menu profile to Writer."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        from louim.template.loader import load_template, TemplateError
        from louim.adapters.writer.menubar import apply_menu_profile
        from louim.adapters.writer.addons import apply_addon_profile

        path = _pick_template(ctx)
        if not path:
            return  # user cancelled

        try:
            template = load_template(path)
        except TemplateError as exc:
            _message_box(ctx, "LOUIM — invalid template", str(exc))
            return

        hidden = apply_menu_profile(ctx, template.get("menus", {}))
        hidden_addons = apply_addon_profile(ctx, template.get("addons", {}))
        name = template.get("profile", {}).get("name") or os.path.basename(path)
        _message_box(
            ctx,
            "LibreOffice UI Manager",
            'Applied "%s".\n\nHidden %d menu(s) and %d extension menu(s).\n'
            "Reopen the document if the menu bar has not refreshed."
            % (name, len(hidden), len(hidden_addons)),
        )
    except Exception as exc:  # noqa: BLE001 — never let a macro crash silently
        _message_box(ctx, "LOUIM error", str(exc))


def restore_menus(*args):
    """Restore Writer's full menu bar and any hidden extension menus."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        from louim.adapters.writer.menubar import restore_default_menus
        from louim.adapters.writer.addons import restore_addon_menus

        restore_default_menus(ctx)
        restore_addon_menus(ctx)
        _message_box(
            ctx,
            "LibreOffice UI Manager",
            "Restored the full Writer interface.\n"
            "Reopen the document if the menu bar has not refreshed.",
        )
    except Exception as exc:  # noqa: BLE001
        _message_box(ctx, "LOUIM error", str(exc))


# Expose the entry points to the LibreOffice script provider.
g_exportedScripts = (hello, apply_template, restore_menus)
