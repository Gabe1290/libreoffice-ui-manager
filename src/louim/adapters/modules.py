# LibreOffice UI Manager — module descriptors.
#
# The Apply Engine is identical across LibreOffice applications; only a handful
# of identifiers differ (the document service, the window-state config node, the
# sidebar context "application" names, and the addon Context service names). A
# ``Module`` bundles those so one engine drives Writer, Calc, and — later —
# Impress and Draw, instead of duplicating every adapter per application.
#
# Pure data (no ``uno``), so it is importable and unit-tested without LibreOffice.


class Module:
    """Application-specific identifiers the adapters need."""

    def __init__(self, key, doc_service, windowstate_node,
                 deck_apps, other_deck_apps, addon_contexts, other_addon_contexts,
                 deck_group_subs=None):
        self.key = key                          # template "application" value
        self.doc_service = doc_service          # module UI config / command labels
        self.windowstate_node = windowstate_node  # toolbar visibility states
        self.deck_apps = tuple(deck_apps)       # sidebar ContextList app groups
        self.other_deck_apps = tuple(other_deck_apps)        # for "any" expansion
        self.addon_contexts = tuple(addon_contexts)          # addon shows here
        self.other_addon_contexts = tuple(other_addon_contexts)  # addon fallback
        # Sidebar context groups shared with another app (e.g. "DrawImpress"
        # covers Draw + Impress): when stripping this module, replace the group
        # with the apps to keep instead of dropping it. {group: (keep, ...)}.
        self.deck_group_subs = dict(deck_group_subs or {})

    def __repr__(self):
        return "Module(%r)" % self.key


WRITER = Module(
    key="writer",
    doc_service="com.sun.star.text.TextDocument",
    windowstate_node="/org.openoffice.Office.UI.WriterWindowState/UIElements/States",
    deck_apps=("WriterVariants", "Writer", "WriterWeb", "WriterGlobal",
               "WriterXForm", "WriterReport", "WriterForm"),
    other_deck_apps=("Calc", "DrawImpress", "Chart", "Math"),
    addon_contexts=("com.sun.star.text.TextDocument",
                    "com.sun.star.text.WebDocument",
                    "com.sun.star.text.GlobalDocument"),
    other_addon_contexts=("com.sun.star.sheet.SpreadsheetDocument",
                          "com.sun.star.presentation.PresentationDocument",
                          "com.sun.star.drawing.DrawingDocument",
                          "com.sun.star.formula.FormulaProperties"),
)

CALC = Module(
    key="calc",
    doc_service="com.sun.star.sheet.SpreadsheetDocument",
    windowstate_node="/org.openoffice.Office.UI.CalcWindowState/UIElements/States",
    deck_apps=("Calc",),
    other_deck_apps=("WriterVariants", "DrawImpress", "Chart", "Math"),
    addon_contexts=("com.sun.star.sheet.SpreadsheetDocument",),
    other_addon_contexts=("com.sun.star.text.TextDocument",
                          "com.sun.star.text.WebDocument",
                          "com.sun.star.text.GlobalDocument",
                          "com.sun.star.presentation.PresentationDocument",
                          "com.sun.star.drawing.DrawingDocument",
                          "com.sun.star.formula.FormulaProperties"),
)

IMPRESS = Module(
    key="impress",
    doc_service="com.sun.star.presentation.PresentationDocument",
    windowstate_node="/org.openoffice.Office.UI.ImpressWindowState/UIElements/States",
    # A deck shows in Impress via the plain "Impress" app or the shared
    # "DrawImpress" group; the group is replaced with "Draw" on strip so the deck
    # stays in Draw.
    deck_apps=("Impress", "DrawImpress"),
    deck_group_subs={"DrawImpress": ("Draw",)},
    other_deck_apps=("WriterVariants", "Calc", "Draw", "Chart", "Math"),
    addon_contexts=("com.sun.star.presentation.PresentationDocument",),
    other_addon_contexts=("com.sun.star.text.TextDocument",
                          "com.sun.star.text.WebDocument",
                          "com.sun.star.text.GlobalDocument",
                          "com.sun.star.sheet.SpreadsheetDocument",
                          "com.sun.star.drawing.DrawingDocument",
                          "com.sun.star.formula.FormulaProperties"),
)

MODULES = {m.key: m for m in (WRITER, CALC, IMPRESS)}


def get_module(key):
    """Return the Module for a template ``application`` key, or None."""
    return MODULES.get(key)


def module_for_document(doc):
    """Return the Module a loaded document belongs to, or None.

    Uses ``supportsService`` so it works for any document object the extension
    has in hand (the current component).
    """
    try:
        for module in MODULES.values():
            if doc.supportsService(module.doc_service):
                return module
    except Exception:  # noqa: BLE001
        pass
    return None
