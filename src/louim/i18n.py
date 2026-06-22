# LibreOffice UI Manager — localization of LOUIM's own UI strings.
#
# The engine is language-independent (it keys on UNO command IDs, never on
# localized labels), so only LOUIM's own dialogs and message boxes need
# translating. Menu titles in Addons.xcu and the Extension Manager name in
# description.xml are localized separately via their own ``xml:lang`` / ``lang``
# attributes; this module covers the runtime strings shown from extension.py.
#
# Supported UI languages: English (default), French, German, Italian. The string
# tables and the ``translator`` are pure Python (no ``uno``) and unit-tested;
# ``office_language`` reads the live Office locale and imports ``uno`` lazily.

DEFAULT_LANG = "en"
SUPPORTED_LANGS = ("en", "fr", "de", "it")

# key -> { lang -> string }. Every non-English string must keep the same
# printf-style placeholders, in the same order, as its English counterpart
# (enforced by the tests) so formatting never fails at runtime.
_STRINGS = {
    "product": {
        "en": "LibreOffice UI Manager",
        "fr": "LibreOffice UI Manager",
        "de": "LibreOffice UI Manager",
        "it": "LibreOffice UI Manager",
    },
    "pick_title": {
        "en": "Choose a LOUIM template",
        "fr": "Choisir un modèle LOUIM",
        "de": "Eine LOUIM-Vorlage auswählen",
        "it": "Scegli un modello LOUIM",
    },
    "filter_louim": {
        "en": "All LOUIM templates (*.louim)",
        "fr": "Tous les modèles LOUIM (*.louim)",
        "de": "Alle LOUIM-Vorlagen (*.louim)",
        "it": "Tutti i modelli LOUIM (*.louim)",
    },
    "filter_module": {
        "en": "%s templates (*.louim)",
        "fr": "Modèles %s (*.louim)",
        "de": "%s-Vorlagen (*.louim)",
        "it": "Modelli %s (*.louim)",
    },
    "filter_all": {
        "en": "All files (*.*)",
        "fr": "Tous les fichiers (*.*)",
        "de": "Alle Dateien (*.*)",
        "it": "Tutti i file (*.*)",
    },
    "apply_body": {
        "en": ('Applied "%s".\n\nHidden %d menu(s), %d extension menu(s), '
               "%d toolbar(s), and %d sidebar deck(s).\n"
               "Reopen the document if the interface has not refreshed."),
        "fr": ("Modèle « %s » appliqué.\n\n%d menu(s), %d menu(s) d'extension, "
               "%d barre(s) d'outils et %d volet(s) latéral(aux) masqués.\n"
               "Rouvrez le document si l'interface ne s'est pas actualisée."),
        "de": ('„%s“ angewendet.\n\n%d Menü(s), %d Erweiterungsmenü(s), '
               "%d Symbolleiste(n) und %d Seitenleisten-Bereich(e) ausgeblendet.\n"
               "Öffnen Sie das Dokument erneut, falls die Oberfläche nicht "
               "aktualisiert wurde."),
        "it": ('Modello "%s" applicato.\n\nNascosti %d menu, %d menu di '
               "estensione, %d barre degli strumenti e %d pannelli della barra "
               "laterale.\nRiapri il documento se l'interfaccia non si è "
               "aggiornata."),
    },
    "invalid_title": {
        "en": "LOUIM — invalid template",
        "fr": "LOUIM — modèle non valide",
        "de": "LOUIM – ungültige Vorlage",
        "it": "LOUIM — modello non valido",
    },
    "wrong_module_body": {
        "en": ("This template is for %s, but the active document is %s.\n"
               "Open a %s document and apply it there."),
        "fr": ("Ce modèle est destiné à %s, mais le document actif est %s.\n"
               "Ouvrez un document %s et appliquez-le là."),
        "de": ("Diese Vorlage ist für %s, aber das aktive Dokument ist %s.\n"
               "Öffnen Sie ein %s-Dokument und wenden Sie sie dort an."),
        "it": ("Questo modello è per %s, ma il documento attivo è %s.\n"
               "Apri un documento %s e applicalo lì."),
    },
    "restore_body": {
        "en": ("Restored the full Writer interface.\n"
               "Reopen the document if the interface has not refreshed."),
        "fr": ("Interface complète de Writer restaurée.\n"
               "Rouvrez le document si l'interface ne s'est pas actualisée."),
        "de": ("Die vollständige Writer-Oberfläche wurde wiederhergestellt.\n"
               "Öffnen Sie das Dokument erneut, falls die Oberfläche nicht "
               "aktualisiert wurde."),
        "it": ("Interfaccia completa di Writer ripristinata.\n"
               "Riapri il documento se l'interfaccia non si è aggiornata."),
    },
    "error_title": {
        "en": "LOUIM error",
        "fr": "Erreur LOUIM",
        "de": "LOUIM-Fehler",
        "it": "Errore LOUIM",
    },
    "save_title": {
        "en": "Save current layout as a LOUIM template",
        "fr": "Enregistrer la disposition actuelle comme modèle LOUIM",
        "de": "Aktuelles Layout als LOUIM-Vorlage speichern",
        "it": "Salva il layout attuale come modello LOUIM",
    },
    "export_body": {
        "en": ('Saved the current layout as "%s".\n\n'
               "It is a plain-text .louim (JSON) file — open it in any text "
               "editor to fine-tune which menus and toolbars are shown, then "
               "share it with other machines via Apply Template..."),
        "fr": ("Disposition actuelle enregistrée sous « %s ».\n\n"
               "C'est un fichier .louim en texte clair (JSON) — ouvrez-le dans "
               "un éditeur de texte pour ajuster les menus et barres d'outils "
               "affichés, puis partagez-le via Appliquer un modèle…"),
        "de": ('Aktuelles Layout als „%s“ gespeichert.\n\n'
               "Dies ist eine Klartext-Datei .louim (JSON) — öffnen Sie sie in "
               "einem Texteditor, um anzupassen, welche Menüs und Symbolleisten "
               "angezeigt werden, und teilen Sie sie dann über „Vorlage "
               "anwenden …“."),
        "it": ('Layout attuale salvato come "%s".\n\n'
               "È un file .louim in testo semplice (JSON) — aprilo in un editor "
               "di testo per regolare quali menu e barre degli strumenti "
               "mostrare, poi condividilo tramite Applica modello…"),
    },
}


def normalize_lang(locale):
    """Reduce an Office locale (e.g. 'fr-CH', 'de-DE') to a supported language.

    Returns one of SUPPORTED_LANGS, defaulting to English for anything we do not
    translate.
    """
    if not locale:
        return DEFAULT_LANG
    lang = str(locale).replace("_", "-").split("-", 1)[0].lower()
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def translator(lang):
    """Return a ``t(key, *args)`` function for ``lang`` (falling back to English).

    Missing keys or languages fall back to English, then to the key itself, so a
    lookup never raises. Positional args are applied with ``%`` formatting.
    """
    lang = normalize_lang(lang)

    def t(key, *args):
        entry = _STRINGS.get(key, {})
        text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
        return text % args if args else text

    return t


def office_language(ctx):
    """Detect the LibreOffice UI language as a supported short code.

    Reads ``ooLocale`` from the Office L10N configuration. Returns 'en' on any
    failure so the UI always has strings.
    """
    try:
        import uno
        provider = ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.configuration.ConfigurationProvider", ctx
        )
        arg = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        arg.Name = "nodepath"
        arg.Value = "/org.openoffice.Setup/L10N"
        access = provider.createInstanceWithArguments(
            "com.sun.star.configuration.ConfigurationAccess", (arg,)
        )
        return normalize_lang(access.getByName("ooLocale"))
    except Exception:  # noqa: BLE001
        return DEFAULT_LANG
