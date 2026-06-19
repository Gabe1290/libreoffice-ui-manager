# LibreOffice UI Manager — Template Manager (loading side).
#
# Reads .louim template files (JSON) into the plain Python structures the rest
# of LOUIM works with. This module does NOT talk to LibreOffice; it only parses
# and lightly validates the file.

import json


class TemplateError(ValueError):
    """Raised when a .louim file is missing or structurally invalid."""


def load_template(path):
    """Load and validate a .louim template file.

    Returns the parsed template as a dict. Raises TemplateError if the file is
    not valid JSON or does not look like a LOUIM template.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise TemplateError("template not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise TemplateError("template is not valid JSON: %s" % exc) from exc

    if not isinstance(data, dict):
        raise TemplateError("template root must be a JSON object")
    if data.get("application") != "writer":
        raise TemplateError(
            "unsupported application: %r (only 'writer' is supported)"
            % data.get("application")
        )

    menus = data.get("menus", {})
    if not isinstance(menus, dict):
        raise TemplateError("'menus' must be a JSON object")
    for command, visible in menus.items():
        if not isinstance(visible, bool):
            raise TemplateError(
                "menu %r must map to true or false, got %r" % (command, visible)
            )

    return data
