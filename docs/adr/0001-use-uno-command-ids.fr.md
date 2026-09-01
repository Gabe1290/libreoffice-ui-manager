# ADR 0001 — Identifier les éléments d'interface par identifiant de commande UNO, jamais par un libellé localisé

*Traduction française de [0001-use-uno-command-ids.md](0001-use-uno-command-ids.md).*

## Statut

Accepté. En vigueur depuis le premier moteur de découverte en v1.0, inchangé
jusqu'à la v4.3.0.

## Contexte

LibreOffice est livré dans de nombreuses langues, et un enseignant et un
élève pourraient utiliser des langues d'interface différentes avec le même
modèle `.louim`. Chaque menu, bouton de barre d'outils et menu d'extension
que LOUIM gère possède à la fois un identifiant interne stable, une URL de
commande UNO comme `.uno:InsertPagebreak`, une URL de ressource de barre
d'outils, ou un nom de nœud de configuration, et un libellé d'affichage que
LibreOffice localise au moment du rendu.

## Décision

Chaque modèle et chaque comparaison interne utilise l'identifiant stable.
Les libellés se résolvent séparément, via `UICommandDescription` (voir
discovery-engine.md), uniquement pour l'affichage, et ne sont jamais écrits
dans un fichier `.louim` ni utilisés pour décider de ce qui est masqué.

## Conséquences

Un modèle `.louim` construit sous un LibreOffice anglais s'applique à
l'identique sous un LibreOffice français, allemand ou italien, sans étape de
traduction et sans variante de modèle par langue. La découverte, l'export et
l'application se fondent tous sur l'identifiant ; les recherches de libellé
peuvent échouer, si `UICommandDescription` n'est pas disponible ou si aucun
cadre de document n'est ouvert, sans casser la logique réelle
d'affichage/masquage. Elles ne dégradent que ce qui est montré à l'humain.
L'outillage existe précisément parce que les identifiants ne sont visibles
nulle part dans l'interface de LibreOffice elle-même. Un enseignant ne peut
pas obtenir `.uno:InsertPagebreak` en regardant un menu, donc
`tools/discover-menus.py` était nécessaire dès le premier jour.

## Où cela vit dans le code

Principe 3 dans `docs/project-constitution.md` ; appliqué dans tout
`src/louim/adapters/writer/*.py`, où chaque fonction de découverte,
d'application et de restauration se fonde sur `command`, `resource`,
`deck`, ou `node`, jamais sur `label`. Les tests i18n vérifient la
cohérence des paramètres mais ne touchent jamais au contenu des modèles.
