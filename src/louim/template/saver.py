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
                      sidebar=None, toolbaritems=None, application="writer"):
    """Build a template dict from a profile name and visibility maps.

    ``menus`` / ``addons`` / ``toolbars`` / ``sidebar`` / ``toolbaritems`` map
    identifiers to booleans, as the discovery snapshots produce. ``application``
    is the module key ("writer"/"calc"). The result is the exact structure
    ``loader`` validates and the Apply Engine consumes. Empty maps for the
    optional sections are still emitted; ``toolbaritems`` is added only when
    non-empty so an exported template stays concise.
    """
    template = {
        "version": TEMPLATE_VERSION,
        "application": application,
        "profile": {
            "name": name or "Untitled",
            "description": description or "",
        },
        "menus": dict(menus or {}),
        "addons": dict(addons or {}),
        "toolbars": dict(toolbars or {}),
        "sidebar": dict(sidebar or {}),
    }
    if toolbaritems:
        template["toolbaritems"] = dict(toolbaritems)
    return template


def save_template(path, template):
    """Write a template dict to ``path`` as formatted JSON.

    Returns ``path``. Raises ``OSError`` if the file cannot be written.
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(template, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def build_current_template(ctx, name, description="", module=None):
    """Snapshot the current interface of ``module`` (default Writer) as a template.

    Reads the live visibility of the menus (item by item), extension menus,
    toolbars, toolbar buttons, and sidebar decks and assembles a template a
    teacher can save and then tweak.
    """
    from louim.adapters.modules import WRITER
    from louim.adapters.writer.menubar import menu_visibility
    from louim.adapters.writer.addons import addon_visibility
    from louim.adapters.writer.toolbars import toolbar_visibility, curate_toolbars
    from louim.adapters.writer.toolbaritems import toolbar_item_visibility
    from louim.adapters.writer.sidebar import sidebar_visibility

    module = module or WRITER
    return assemble_template(
        name,
        description,
        menus=menu_visibility(ctx, module),
        addons=addon_visibility(ctx, module),
        toolbars=curate_toolbars(toolbar_visibility(ctx, module)),
        sidebar=sidebar_visibility(ctx, module),
        toolbaritems=toolbar_item_visibility(ctx, module),
        application=module.key,
    )
