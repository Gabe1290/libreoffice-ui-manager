# ADR 0003 — Pas de classe `UIElement` unifiée ; une carte identifiant-vers-booléen par surface

*Traduction française de [0003-ui-element-model.md](0003-ui-element-model.md).*

## Statut

Accepté, remplaçant le modèle `UIElement` unifié dans
`docs/project-constitution.md`, principe 5. En vigueur depuis que
l'adaptateur de barres d'outils a été ajouté au moteur d'application v2, ce
qui a établi le modèle que les surfaces ultérieures (boutons de barre
d'outils, barre latérale, menus d'extension) ont toutes suivi.

## Contexte

La couche Modèle de la constitution nomme un type unique `UIElement` censé
représenter, génériquement, un élément d'interface que LOUIM peut afficher
ou masquer : menus, barres d'outils, et tout ce qui serait ajouté plus tard.
Au fur et à mesure que les barres d'outils, les boutons de barre d'outils
individuels, les volets de la barre latérale et les menus d'extension ont
été effectivement construits, chacun s'est révélé avoir besoin d'un
mécanisme de stockage réellement différent. Les menus ont besoin d'un arbre
de configuration à réinitialiser et élaguer, indexé par identifiant de
commande UNO. Les barres d'outils ont besoin d'un simple drapeau `Visible`
par URL de ressource dans la configuration d'état de fenêtre. Les boutons de
barre d'outils ont besoin du même type d'arbre de configuration que les
menus, mais par barre d'outils. Les volets de la barre latérale ont besoin
d'une liste de chaînes partagée (`ContextList`) par volet, éditée de façon
compositionnelle parce qu'elle est partagée entre applications. Les menus
d'extension ont besoin d'une chaîne partagée séparée par virgules
(`Context`) par nœud, éditée de la même façon compositionnelle que les
volets de la barre latérale, pour la même raison.

Une classe `UIElement` unique couvrant les cinq aurait eu besoin soit d'une
grande union de champs optionnels, où la plupart des champs seraient dénués
de sens pour la plupart des instances, soit d'une sous-classe par surface
qui finit par faire tout le vrai travail de toute façon, auquel cas la
classe de base n'apporte pas grand-chose au-delà d'un nom.

## Décision

Pas de classe `UIElement`. Chaque surface garde son propre espace de noms
d'identifiants, identifiant de commande UNO, URL de ressource de barre
d'outils, identifiant de volet, ou nom de nœud de menu d'extension, et sa
propre carte plate `{identifiant : booléen}`, aussi bien en mémoire que dans
le format de fichier `.louim` (`menus`, `toolbars`, `toolbaritems`,
`sidebar`, `addons` — cinq clés de premier niveau indépendantes ; voir
[template-format.md](../template-format.md)). Ce qui est réellement partagé
entre les cinq n'est pas une classe de base, c'est comportemental : la forme
des fonctions de découverte, d'application et de restauration documentée
dans [ui-element-model.md](../ui-element-model.md) et
[discovery-engine.md](../discovery-engine.md).

## Conséquences

Ajouter une sixième surface signifie ajouter un sixième module adaptateur
et une sixième section de modèle, pas modifier une classe partagée. Cela
s'est vérifié pour les quatre surfaces ajoutées après les menus, barres
d'outils, boutons de barre d'outils, barre latérale et menus d'extension,
chacune livrée dans sa propre version. Deux surfaces, les menus et les
boutons de barre d'outils, partagent directement du code via
`menubar._prune_hidden`, parce que leur stockage a réellement la même
forme. La réutilisation suit ici la ressemblance structurelle, elle n'est
pas forcée par une interface commune. Le format `.louim` reste facile à
éditer à la main, un objectif depuis la v1, parce que chaque section est une
simple carte plate sans discriminant de type d'élément imbriqué à bien
gérer. Un outil d'interface générique qui voudrait afficher « tous les
éléments d'interface » dans une seule liste aurait besoin de fusionner
lui-même cinq cartes indexées différemment. Les propres boîtes de dialogue
de LOUIM, comme Configurer les menus, n'opèrent jamais que sur une seule
surface à la fois, donc cela n'a pas représenté un coût réel en pratique.

## Où cela vit dans le code

`src/louim/adapters/writer/menubar.py`, `toolbars.py`, `toolbaritems.py`,
`sidebar.py`, et `addons.py` — cinq modules indépendants, sans classe de
base partagée et sans import entre eux, à l'exception de `toolbaritems.py`
qui réutilise `menubar._prune_hidden`.
