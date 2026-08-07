# Security Policy

LOUIM only ever changes LibreOffice **UI configuration** (menus, toolbar
visibility, sidebar decks, extension-menu contexts). It must never touch
documents, rendering/graphics settings, or anything outside the user profile's
UI state. A `.louim` template is plain JSON that is parsed and validated — it
contains no executable content.

## Reporting a vulnerability

If you find a way to make LOUIM do more than the above — or any other security
concern — please report it privately via
[GitHub security advisories](https://github.com/Gabe1290/libreoffice-ui-manager/security/advisories/new)
rather than a public issue. You should receive a response within two weeks.
