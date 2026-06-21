# LibreOffice UI Manager — Template Manager (saving side).
#
# The mirror of loader.py: turns LOUIM's plain Python structures back into a
# .louim file, and snapshots Writer's *current* interface into a template so a
# teacher can export what they have set up and then edit the JSON by hand.
#
# ``save_template`` and ``assemble_template`` are pure Python (no LibreOffice),
# so they are unit-tested in CI. ``build_current_template`` reads the live
# interface and therefore imports the Writer adapters lazily, exactly as the
# extension entry points do.

import json

TEMPLATE_VERSION = 1


def assemble_template(name, description, menus, addons=None, toolbars=None,
                      sidebar=None):
    """Build a template dict from a profile name and visibility maps.

    ``menus`` / ``addons`` / ``toolbars`` / ``sidebar`` map identifiers to
    booleans, as the discovery snapshots produce. The result is the exact
    structure ``loader`` validates and the Apply Engine consumes.
    """
    return {
        "version": TEMPLATE_VERSION,
        "application": "writer",
        "profile": {
            "name": name or "Untitled",
            "description": description or "",
        },
        "menus": dict(menus or {}),
        "addons": dict(addons or {}),
        "toolbars": dict(toolbars or {}),
        "sidebar": dict(sidebar or {}),
    }


def save_template(path, template):
    """Write a template dict to ``path`` as formatted JSON.

    Returns ``path``. Raises ``OSError`` if the file cannot be written.
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(template, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def build_current_template(ctx, name, description=""):
    """Snapshot Writer's current interface as a template dict.

    Reads the live visibility of the top-level menus, extension menus, and
    toolbars and assembles a template a teacher can save and then tweak.
    """
    from louim.adapters.writer.menubar import menu_visibility
    from louim.adapters.writer.addons import addon_visibility
    from louim.adapters.writer.toolbars import toolbar_visibility
    from louim.adapters.writer.sidebar import sidebar_visibility

    return assemble_template(
        name,
        description,
        menus=menu_visibility(ctx),
        addons=addon_visibility(ctx),
        toolbars=toolbar_visibility(ctx),
        sidebar=sidebar_visibility(ctx),
    )
