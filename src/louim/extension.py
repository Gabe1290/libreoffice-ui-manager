# LibreOffice UI Manager — extension entry points.
#
# These functions are the bridge between the LibreOffice menu (Addons.xcu) and
# the LOUIM engine. Each is exported through ``g_exportedScripts`` so the bundled
# Python script provider can invoke it from a ``vnd.sun.star.script:`` menu URL.
#
# The engine itself (discovery, template loading, apply/restore) lives in the
# ``louim`` package and is unit/headlessly tested separately. This module only
# handles the LibreOffice-facing glue: file picking and message boxes. All
# user-visible strings are localized through ``louim.i18n`` (en/fr/de/it).

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


def _translator(ctx):
    """Return a localized ``t(key, *args)`` for the current Office language.

    Requires the bundled package on ``sys.path`` (call ``_ensure_package_path``
    first). Falls back to an English translator if anything goes wrong.
    """
    try:
        from louim.i18n import translator, office_language
        return translator(office_language(ctx))
    except Exception:  # noqa: BLE001
        from louim.i18n import translator
        return translator("en")


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


def _error_box(ctx, exc):
    """Show an error box with a localized title, with a hard English fallback."""
    try:
        title = _translator(ctx)("error_title")
    except Exception:  # noqa: BLE001
        title = "LOUIM error"
    _message_box(ctx, title, str(exc))


def _pick_template(ctx, t):
    """Open a file picker for a .louim template; return a system path or None."""
    from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

    smgr = ctx.getServiceManager()
    picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker", ctx
    )
    picker.setTitle(t("pick_title"))
    picker.appendFilter(t("filter_louim"), "*.louim")
    picker.appendFilter(t("filter_all"), "*.*")

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


def _pick_save_path(ctx, t):
    """Open a Save dialog for a new .louim template; return a path or None."""
    from com.sun.star.ui.dialogs.ExecutableDialogResults import OK
    from com.sun.star.ui.dialogs.TemplateDescription import (
        FILESAVE_AUTOEXTENSION,
    )

    smgr = ctx.getServiceManager()
    picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker", ctx
    )
    picker.initialize((FILESAVE_AUTOEXTENSION,))
    picker.setTitle(t("save_title"))
    picker.appendFilter(t("filter_louim"), "*.louim")
    picker.setCurrentFilter(t("filter_louim"))
    picker.setDefaultName("my-template.louim")

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
        _ensure_package_path(ctx)
        t = _translator(ctx)
        _message_box(ctx, t("product"), t("hello_body"))
    except Exception as exc:  # noqa: BLE001 — surface any glue failure to the log
        print("LOUIM error:", exc)


def apply_template(*args):
    """Pick a .louim template and apply its menu profile to Writer."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        from louim.template.loader import load_template, TemplateError
        from louim.adapters.writer.menubar import apply_menu_profile
        from louim.adapters.writer.addons import apply_addon_profile
        from louim.adapters.writer.toolbars import apply_toolbar_profile
        from louim.adapters.writer.sidebar import apply_sidebar_profile

        path = _pick_template(ctx, t)
        if not path:
            return  # user cancelled

        try:
            template = load_template(path)
        except TemplateError as exc:
            _message_box(ctx, t("invalid_title"), str(exc))
            return

        hidden = apply_menu_profile(ctx, template.get("menus", {}))
        hidden_addons = apply_addon_profile(ctx, template.get("addons", {}))
        hidden_toolbars = apply_toolbar_profile(ctx, template.get("toolbars", {}))
        hidden_decks = apply_sidebar_profile(ctx, template.get("sidebar", {}))
        name = template.get("profile", {}).get("name") or os.path.basename(path)
        _message_box(
            ctx,
            t("product"),
            t("apply_body", name, len(hidden), len(hidden_addons),
              len(hidden_toolbars), len(hidden_decks)),
        )
    except Exception as exc:  # noqa: BLE001 — never let a macro crash silently
        _error_box(ctx, exc)


def restore_menus(*args):
    """Restore Writer's full menu bar and any hidden extension menus."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        from louim.adapters.writer.menubar import restore_default_menus
        from louim.adapters.writer.addons import restore_addon_menus
        from louim.adapters.writer.toolbars import restore_toolbars
        from louim.adapters.writer.sidebar import restore_sidebar_decks

        restore_default_menus(ctx)
        restore_addon_menus(ctx)
        restore_toolbars(ctx)
        restore_sidebar_decks(ctx)
        _message_box(ctx, t("product"), t("restore_body"))
    except Exception as exc:  # noqa: BLE001
        _error_box(ctx, exc)


def export_template(*args):
    """Snapshot Writer's current interface and save it as a .louim template."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        from louim.template.saver import build_current_template, save_template

        path = _pick_save_path(ctx, t)
        if not path:
            return  # user cancelled

        name = os.path.splitext(os.path.basename(path))[0]
        template = build_current_template(ctx, name=name)
        save_template(path, template)
        _message_box(ctx, t("product"), t("export_body", os.path.basename(path)))
    except Exception as exc:  # noqa: BLE001
        _error_box(ctx, exc)


# Expose the entry points to the LibreOffice script provider.
g_exportedScripts = (hello, apply_template, restore_menus, export_template)
