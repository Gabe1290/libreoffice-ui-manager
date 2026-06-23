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

# Subfolder of the user's "My Documents" where the Save dialog defaults, so
# teacher-made templates land in a durable, user-owned place (the per-user
# extension cache is wiped on every reinstall/update). Deliberately NOT
# localized: a stable folder name avoids scattering templates across several
# language-specific folders when the UI language changes.
_SAVE_SUBDIR = "LOUIM templates"


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


def _current_module(ctx):
    """The LOUIM Module for the active document (Writer/Calc), or Writer.

    Requires the bundled package on ``sys.path``. The LOUIM menu appears in each
    supported application, so apply/restore/export act on whichever you are in.
    """
    from louim.adapters.modules import module_for_document, WRITER
    try:
        doc = XSCRIPTCONTEXT.getDesktop().getCurrentComponent()
        return module_for_document(doc) or WRITER
    except Exception:  # noqa: BLE001
        return WRITER


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


def _templates_dir_url(ctx, module):
    """File URL of the bundled templates folder to open the picker in, or None.

    Filter by *location*, not by filename pattern: the starter templates are
    bundled in per-application subfolders (``templates/writer/`` etc.), so
    opening the picker in the active app's subfolder shows only that app's
    templates. This is what the native file dialog can do reliably -- it filters
    by extension and by the folder it lands in, but silently ignores prefix
    globs like ``writer-*.louim``. (The cross-platform wildcard alternative,
    ``OfficeFilePicker``, hits a Skia list-rendering glitch on locked-down Linux
    where filenames fail to paint, so it is not an option here.)

    Falls back to the templates root if the per-module subfolder is missing, and
    to ``None`` (picker opens at its last location) if nothing resolves.
    """
    url = _package_url(ctx)
    if not url:
        return None
    root = url.rstrip("/") + "/templates"
    for candidate in (root + "/" + module.key, root):
        try:
            if os.path.isdir(uno.fileUrlToSystemPath(candidate)):
                return candidate
        except Exception:  # noqa: BLE001
            continue
    return None


def _pick_template(ctx, t, module):
    """Open a file picker for a .louim template; return a system path or None.

    Opens in the active application's bundled templates subfolder so e.g. Writer
    shows only Writer templates (folder-based filtering -- see
    ``_templates_dir_url``). Navigating up one folder reveals every app's
    templates, which is the "all templates" escape hatch.
    """
    from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

    smgr = ctx.getServiceManager()
    # Native picker (renders correctly under locked-down school defaults).
    picker = smgr.createInstanceWithContext(
        "com.sun.star.ui.dialogs.FilePicker", ctx
    )
    picker.setTitle(t("pick_title"))
    picker.appendFilter(t("filter_louim"), "*.louim")
    picker.appendFilter(t("filter_all"), "*.*")
    picker.setCurrentFilter(t("filter_louim"))

    # Land in the active app's templates subfolder so the listing is already
    # scoped to that application. Best-effort: if it can't be located the picker
    # just opens at its last location.
    templates_url = _templates_dir_url(ctx, module)
    if templates_url:
        picker.setDisplayDirectory(templates_url)

    if picker.execute() != OK:
        return None
    files = picker.getSelectedFiles()
    return uno.fileUrlToSystemPath(files[0]) if files else None


def _documents_save_url(ctx):
    """File URL of ``<My Documents>/LOUIM templates`` (created if needed), or None.

    Teacher-made templates belong in a durable, user-owned location, not the
    per-user extension cache (which is wiped on every reinstall/update). Uses
    LibreOffice's configured "My Documents" path (``$(work)``), which is what the
    user sees as their documents folder elsewhere in the app, then a stable
    ``LOUIM templates`` subfolder under it. Best-effort: falls back to Documents
    itself, then to ``None`` (picker opens at its last location).
    """
    try:
        smgr = ctx.getServiceManager()
        subst = smgr.createInstanceWithContext(
            "com.sun.star.util.PathSubstitution", ctx
        )
        work_path = uno.fileUrlToSystemPath(
            subst.substituteVariables("$(work)", True)
        )
    except Exception:  # noqa: BLE001
        return None

    target = os.path.join(work_path, _SAVE_SUBDIR)
    try:
        os.makedirs(target, exist_ok=True)
        if os.path.isdir(target):
            return uno.systemPathToFileUrl(target)
        if os.path.isdir(work_path):
            return uno.systemPathToFileUrl(work_path)
    except Exception:  # noqa: BLE001
        pass
    return None


def _pick_save_path(ctx, t, module):
    """Open a Save dialog for a new .louim template; return a path or None.

    Defaults the file name to ``<app>-my-template.louim`` (the app prefix keeps
    saved templates self-describing) and the directory to the user's
    ``Documents/LOUIM templates`` folder so they persist across reinstalls.
    """
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
    picker.setDefaultName("%s-my-template.louim" % module.key)

    # Default into the user's Documents/LOUIM templates folder so teacher-made
    # templates persist (the extension cache is wiped on reinstall/update).
    save_url = _documents_save_url(ctx)
    if save_url:
        picker.setDisplayDirectory(save_url)

    if picker.execute() != OK:
        return None
    files = picker.getSelectedFiles()
    return uno.fileUrlToSystemPath(files[0]) if files else None


def apply_template(*args):
    """Pick a .louim template and apply its profile to the active application."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        module = _current_module(ctx)
        from louim.template.loader import load_template, TemplateError
        from louim.adapters.writer.menubar import apply_menu_profile
        from louim.adapters.writer.addons import apply_addon_profile
        from louim.adapters.writer.toolbars import apply_toolbar_profile
        from louim.adapters.writer.toolbaritems import (
            apply_toolbar_items, hidden_toolbar_commands,
        )
        from louim.adapters.writer.sidebar import apply_sidebar_profile

        path = _pick_template(ctx, t, module)
        if not path:
            return  # user cancelled

        try:
            template = load_template(path)
        except TemplateError as exc:
            _message_box(ctx, t("invalid_title"), str(exc))
            return

        # The template must target the application you are in.
        if template.get("application") != module.key:
            _message_box(ctx, t("invalid_title"),
                         t("wrong_module_body",
                           str(template.get("application")).capitalize(),
                           module.key.capitalize(), module.key.capitalize()))
            return

        hidden = apply_menu_profile(ctx, template.get("menus", {}), module)
        hidden_addons = apply_addon_profile(ctx, template.get("addons", {}), module)
        hidden_toolbars = apply_toolbar_profile(
            ctx, template.get("toolbars", {}), module)
        apply_toolbar_items(ctx, hidden_toolbar_commands(ctx, template, module),
                            module)
        hidden_decks = apply_sidebar_profile(
            ctx, template.get("sidebar", {}), module)
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
    """Restore the active application's full menus, toolbars, and sidebar."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        module = _current_module(ctx)
        from louim.adapters.writer.menubar import restore_default_menus
        from louim.adapters.writer.addons import restore_addon_menus
        from louim.adapters.writer.toolbars import restore_toolbars
        from louim.adapters.writer.toolbaritems import restore_toolbar_items
        from louim.adapters.writer.sidebar import restore_sidebar_decks

        restore_default_menus(ctx, module)
        restore_addon_menus(ctx, module)
        restore_toolbars(ctx, module)
        restore_toolbar_items(ctx, module)
        restore_sidebar_decks(ctx, module)
        _message_box(ctx, t("product"), t("restore_body"))
    except Exception as exc:  # noqa: BLE001
        _error_box(ctx, exc)


def export_template(*args):
    """Snapshot the active application's interface and save it as a template."""
    ctx = XSCRIPTCONTEXT.getComponentContext()
    try:
        _ensure_package_path(ctx)
        t = _translator(ctx)
        module = _current_module(ctx)
        from louim.template.saver import build_current_template, save_template

        path = _pick_save_path(ctx, t, module)
        if not path:
            return  # user cancelled

        name = os.path.splitext(os.path.basename(path))[0]
        template = build_current_template(ctx, name=name, module=module)
        save_template(path, template)
        _message_box(ctx, t("product"), t("export_body", os.path.basename(path)))
    except Exception as exc:  # noqa: BLE001
        _error_box(ctx, exc)


# Expose the entry points to the LibreOffice script provider.
g_exportedScripts = (apply_template, restore_menus, export_template)
