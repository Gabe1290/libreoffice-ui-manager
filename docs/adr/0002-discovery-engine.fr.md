# ADR 0002 — Découvrir l'interface active ; ne jamais la coder en dur

*Traduction française de [0002-discovery-engine.md](0002-discovery-engine.md).*

## Statut

Accepté. En vigueur depuis la v1.0.

## Contexte

Une alternative à la lecture de la configuration propre de LibreOffice
aurait été de livrer une table intégrée des menus, barres d'outils et
commandes connus par version de LibreOffice. Cette table aurait dû être mise
à jour à chaque nouvelle version de LibreOffice, elle aurait raté tout ce
qu'une extension comme Dmaths ou la propre personnalisation d'un enseignant
via Outils ▸ Personnaliser apportait, et elle se serait silencieusement
décalée de la réalité avec le temps.

## Décision

Chaque fonction `discover_*` et `*_visibility` lit la configuration active
de LibreOffice au moment de l'appel : le gestionnaire de configuration UI du
module pour les menus et les barres d'outils, la configuration d'état de
fenêtre pour la visibilité des barres d'outils, la configuration Sidebar
pour les volets, la configuration Addons pour les menus d'extension. Rien de
ce que LOUIM peut voir de l'interface n'est intégré comme table statique.
Voir [discovery-engine.md](../discovery-engine.md) pour la carte complète
des fonctions.

## Conséquences

LOUIM voit automatiquement tout ce que le LibreOffice en service possède
réellement comme menus, barres d'outils, volets et menus d'extension, y
compris les menus d'extension tiers et tout ce qu'un enseignant a retiré à
la main avant d'exporter. La fonctionnalité « Enregistrer la disposition
comme modèle... » dépend directement de cela. Il n'y a aucune charge de
maintenance à suivre la structure des menus de LibreOffice d'une version à
l'autre ; un appel de découverte contre un LibreOffice plus récent renvoie
simplement ce que cette version possède réellement. Le compromis est que
chaque appel de découverte ou d'export a besoin d'un contexte UNO en
service. Il n'existe pas de repli hors ligne pour « à quoi ressemble la
barre de menus de Writer en ce moment ». C'est pourquoi les outils de
développement existent : trouver un identifiant à mettre dans un modèle
signifie réellement interroger une instance en service, conformément aux
règles de sécurité dans [CLAUDE.md](../../CLAUDE.md), une instance headless
jetable, jamais celle de l'utilisateur.

## Où cela vit dans le code

Principe 4 dans `docs/project-constitution.md` — « Les définitions
d'interface codées en dur ne devraient être utilisées que comme repli de
compatibilité », et en pratique aucune n'existe. Chaque fonction
`discover_*` et `*_visibility` dans `src/louim/adapters/writer/*.py`.
