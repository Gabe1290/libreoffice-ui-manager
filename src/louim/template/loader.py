# LibreOffice UI Manager — Template Manager (loading side).
#
# Reads .louim template files (JSON) into the plain Python structures the rest
# of LOUIM works with. This module does NOT talk to LibreOffice; it only parses
# and lightly validates the file.

import json

# Highest .louim format version this LOUIM understands. Lives here (not in
# saver.py) because the loader is the compatibility gate; the saver imports it.
TEMPLATE_VERSION = 1

# Template "application" values LOUIM can apply (LibreOffice module keys).
SUPPORTED_APPLICATIONS = ("writer", "calc", "impress", "draw")


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

    # A missing version means the original (v1) format; a newer one means the
    # file was made for a newer LOUIM and applying it partially would be worse
    # than refusing.
    version = data.get("version", TEMPLATE_VERSION)
    if not isinstance(version, int) or isinstance(version, bool):
        raise TemplateError("'version' must be an integer, got %r" % version)
    if version > TEMPLATE_VERSION:
        raise TemplateError(
            "template version %d is newer than this LOUIM supports (up to %d) "
            "— update the extension" % (version, TEMPLATE_VERSION)
        )

    if data.get("application") not in SUPPORTED_APPLICATIONS:
        raise TemplateError(
            "unsupported application: %r (supported: %s)"
            % (data.get("application"), ", ".join(SUPPORTED_APPLICATIONS))
        )

    profile = data.get("profile", {})
    if not isinstance(profile, dict):
        raise TemplateError("'profile' must be a JSON object")
    for field in ("name", "description"):
        if not isinstance(profile.get(field, ""), str):
            raise TemplateError(
                "profile %r must be a string, got %r" % (field, profile.get(field))
            )

    _validate_bool_map(data.get("menus", {}), "menus", "menu")
    _validate_bool_map(data.get("addons", {}), "addons", "addon")
    _validate_bool_map(data.get("toolbars", {}), "toolbars", "toolbar")
    _validate_bool_map(data.get("toolbaritems", {}), "toolbaritems", "toolbar item")
    _validate_bool_map(data.get("sidebar", {}), "sidebar", "sidebar deck")

    flag = data.get("hide_toolbar_buttons_with_menus", False)
    if not isinstance(flag, bool):
        raise TemplateError(
            "'hide_toolbar_buttons_with_menus' must be true or false, got %r"
            % flag
        )

    return data


def _validate_bool_map(value, field, item):
    """Validate that ``value`` is a JSON object mapping strings to booleans."""
    if not isinstance(value, dict):
        raise TemplateError("'%s' must be a JSON object" % field)
    for key, visible in value.items():
        if not isinstance(visible, bool):
            raise TemplateError(
                "%s %r must map to true or false, got %r" % (item, key, visible)
            )
